import pandas as pd
import config
from catalyst.models import CleansingRule, Entity, EntityField, Customer, GoLive
from catalyst.loadfiles import get_loadfile
from app import db
import json
from cerberus import Validator


def generate_data_issues(golive):
    # clear all issues
    conn = config.sql_connect(golive.customer.database_name)
    conn = conn.connect()

    with conn:
        conn.execute('delete from reporting.MO01_Customer')


    #TODO: pandas issues not working atm, but didn't want to remove for later use
    #pandas_issues = generate_cerberus_data_issues()
    issues = generate_cerberus_data_issues(rules)

    conn = config.sql_connect(golive.customer.database_name)
    conn = conn.connect()

    with conn:
        issues.to_sql('data_cleaning_issues', conn, if_exists='replace', index=False, schema='reporting')


def create_cerberus_validation_dict(entity_id):
    # fetch all the rules
    rules = CleansingRule.query.filter_by(entity_id=entity_id)
    rules_df = pd.read_sql(rules.statement, rules.session.bind)

    # fetch number fields
    fields = rules_df.entity_field_id.unique()

    # prep entity valdiation dict
    entity_validation = []

    # build validation dict for every field
    for f in fields:
        field = EntityField.query.get(str(f))       # convert to str or else you get errors
        dic = {}

        for r in rules:
            rule = r.rule
            criteria = r.criteria
            try:
                criteria = int(criteria)
            except TypeError:
                pass
            except ValueError:
                pass

            # set true/false criteria
            if criteria == 'False':
                criteria = False
            if criteria == 'True':
                criteria = True

            row_dic = {rule: criteria}
            print(row_dic)
            dic.update(row_dic)

        validation_dict = {field.field: dic}
        entity_validation.append(validation_dict)

    print(entity_validation)

    # store validation dict
    entity = Entity.query.get(entity_id)
    entity.data_cleansing_json = str(entity_validation)
    db.session.commit()


def generate_cerberus_data_issues(entity_id):
    # fetch entity
    entity = Entity.query.get(entity_id)

    # fetch loadfile
    df = get_loadfile(entity_id)
    validation_dict = json.loads(entity.data_cleansing_json)
    print(validation_dict)

    v = Validator(validation_dict)
    v.allow_unknown = True

    dic = df.to_dict(orient='records')
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

    df['validation_succesful'] = validation_succesful
    df['errors'] = errors

    print(df)

    # return issues


def generate_pandas_data_issues(rules):

    issues = pd.DataFrame(columns=['code', 'rule_id', 'golive', 'entity', 'field', 'issue', 'value'])

    for r in rules:
        field = EntityField.query.filter_by(id=r.entity_field).first()
        entity = Entity.query.filter_by(id=field.entity_id).first()

        df = get_loadfile(entity.entity_id)

        issue = pd.DataFrame(columns=['code', 'issue', 'value'])

        df_filtered = df.query(r.rule, engine='python')[[field.field]]
        issue['value'] = df_filtered[field.field]
        issue['issue'] = r.description
        issue['rule_id'] = r.id
        issue['entity'] = entity.entity_id
        issue['field'] = field.field
        issue['golive'] = entity.golive_id
        # df_filtered = df_filtered.rename(columns={field: "value"})

        issues = issues.append(issue)

    issues.to_csv('test.csv', index=False)

    return issues