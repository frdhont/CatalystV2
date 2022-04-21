from catalyst.models import EntityField, Entity, GoLive
from app import db
import json
from cerberus import Validator
import config


def validate_loadfile(loadfile, entity):
    if entity.validation_json is not None:
        print('### Validating entity ' + entity.entity)
        v = Validator()
        v.schema = json.loads(entity.validation_json)
        v.allow_unknown = entity.allow_unknown

        dic = loadfile.to_dict(orient='records')
        validation_succesful = []
        errors = []
        error_count = 0
        for item in dic:
            if v.validate(item):
                val = True
                error = None
            else:
                error_count = error_count + 1
                error = json.dumps(v.errors)
                val = False
            validation_succesful.append(val)
            errors.append(error)

        print('## ' + str(error_count) + ' errors found on ' + entity.entity)

        loadfile['validation_succesful'] = validation_succesful
        loadfile['errors'] = errors
    else:
        print('### Skipping validation, no validation json set for ' + entity.entity)
        loadfile['validation_succesful'] = True
        loadfile['errors'] = None
    return loadfile


def create_validation_dict(entity_id):
    ent = Entity.query.get(entity_id)
    fields = EntityField.query.filter_by(entity_id=entity_id)

    val = {}

    for field in fields:
        field_dic = {'type': field.type, 'empty': field.allow_null}
        val[field.field] = field_dic

        if field.regex_validation is not None and field.regex_validation != '':
            field_dic = {'regex': field.regex_validation}
        val[field.field] = field_dic

    ent.validation_json = json.dumps(val)
    db.session.commit()




