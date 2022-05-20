from catalyst.models import EntityField, Translation, ParameterQuery
import pandas as pd
from catalyst.loadfiles.source_data import get_source_data
from collections import defaultdict
import numpy as np

def map_entity(entity):
    print('### Mapping ' + entity.entity + ' for golive ' + entity.golive_id)

    # fetch fields that need to be mapped
    fields = EntityField.query.filter_by(entity_id=entity.id)
    # fields = EntityField.entity.has(id=entity.id)
    # print(fields)

    if fields.count() > 0:
        field_list = [r.field for r in fields]

        # fetch source data & remove out of scope records
        if entity.scope_column is not None:
            source_data = get_source_data(entity).query(entity.scope_column + ' == True')
            # print(source_data)
        else:
            source_data = get_source_data(entity)

        # print(source_data)
        df = pd.DataFrame(columns=field_list)

        # map all fields except default & parameter
        for field in fields:
            field_name = field.field
            source_field = field.source_field

            if field.mapping_type == 'one_to_one':
                if source_field is None or source_field == '':
                    print('## Warning: field ' + field_name + ' set to one to one, but no source field set')
                    df[field_name] = 'No source field'
                else:
                    print('## Setting field ' + field_name + ' one to one equal to source field ' + field.source_field)
                    df[field_name] = source_data[source_field]

            if field.mapping_type == 'translation':
                translation_key = field.translation_key
                if translation_key is None or translation_key == '':
                    print('## Warning: field ' + field_name + ' set to translation, but no translation key set')
                    df[field_name] = 'No translation key'
                elif source_field is None or source_field == '':
                    print('## Warning: field ' + field_name + ' set to translation, but no source field set')
                    df[field_name] = 'No source field'
                else:
                    print('## Setting field ' + field_name + ' as translation from source field ' + field.source_field + ' with key ' + translation_key)

                    translations = Translation.query.filter_by(translation_key=translation_key).with_entities(Translation.from_value, Translation.to_value)
                    # print(translations)
                    if translations.count() == 0:
                        print('## Warning: no translations of type ' + field.translation_key + ' found for field ' + field_name)
                        df[field_name] = 'No translations found'
                    else:
                        # create default dict if default value is set
                        if field.default_value is not None:
                            dic = defaultdict(lambda: field.default_value)
                        else:
                            dic = {}

                        # transform results to pandas & dict to be able to do translations
                        t = pd.read_sql(translations.statement, translations.session.bind)
                        t.set_index('from_value', drop=True, inplace=True)
                        t = t.to_dict()['to_value']
                        dic.update(t)

                        # translate values for which there is a translation
                        df[field_name] = source_data[source_field].map(dic)

            if field.mapping_type == 'transformation':
                lam = 'lambda x:' + field.transformation_rule
                print('## Setting field ' + field_name + ' as calculation from transformation rule: \'' + lam + '\'')
                try:
                    df[field_name] = source_data[source_field].apply(eval(lam))
                    # print(s)
                except SyntaxError as e:
                    df[field_name] = '## Invalid syntax ##'
                    print('Invalid lambda syntax')
                    pass

            if field.mapping_type == 'number_sequence':
                start = field.number_sequence.start
                stop = start + len(source_data)
                length = field.number_sequence.length
                prefix = field.number_sequence.prefix
                print(
                    '## Generating number sequence for field ' + field_name +
                    '. Format: ' + prefix + str(start).zfill(length))
                seq = pd.Series(np.arange(start=start, stop=stop))  # create series
                seq = seq.apply(lambda x: prefix + (str(x).zfill(length)))  # apply leading zeros + prefix
                df[field_name] = seq

            # remove fields that have already been processed
            # fields.pop(field)

        # map default & parameter fields last
        for field in fields:
            field_name = field.field

            if field.mapping_type == 'parameter':
                # fetch parameter value
                param = ParameterQuery.get_parameter(parameter=field.parameter, golive_id=field.golive_id
                                                     , customer_id=entity.golive.customer_id)
                print('## Setting field ' + field_name + ' to value of parameter \'' + str(field.parameter) + '\': \'' + str(param) + '\'')
                df[field_name] = param

            if field.mapping_type == 'default':
                print('## Setting field ' + field_name + ' to default \'' + str(field.default_value) + '\'')
                df[field_name] = field.default_value


        # add code field
        df['code'] = source_data[entity.code_column]
        df.insert(0, 'code', df.pop('code'))
        # print(df)

        return df

    return
