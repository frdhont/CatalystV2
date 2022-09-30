import pandas as pd
import config
from catalyst.models import CleansingRule, Entity, EntityField, Customer, GoLive
from catalyst.loadfiles import get_loadfile
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import and_
from app import db
import json
from cerberus import Validator
from flask_login import current_user


def generate_data_issues(golive_id):
    golive = GoLive.query.get(golive_id)

    # clear all issues
    conn = config.sql_connect(golive.customer.database_name)
    conn = conn.connect()

    try:
        with conn:
            conn.execute('delete from reporting.data_issues where golive = \'' + golive_id + '\'')
    except ProgrammingError as e:
        print('Table reporting.data_issues doesn\'t exist yet')
        # print(e)

    # fetch applicable rules for golive
    rules = CleansingRule.query.filter_by(golive_id=golive.id)

    # fetch distinct entities
    entities = set([r.entity_id for r in rules])

    print('Generating data issues for ' + golive.id)
    for entity_id in entities:
        create_cerberus_validation_dict(entity_id)
        generate_cerberus_data_issues(entity_id)
        # TODO: pandas issues not working atm, but didn't want to remove for later use
        # pandas_issues = generate_cerberus_data_issues(entity_id)


def create_cerberus_validation_dict(entity_id):
    # fetch all the rules
    rules = CleansingRule.query.filter(and_(CleansingRule.entity_id == entity_id, CleansingRule.type == 'cerberus'
                                            , CleansingRule.active == 'True'))
    rules_df = pd.read_sql(rules.statement, rules.session.bind)

    # fetch number fields
    fields = set([r.entity_field_id for r in rules])  # set() in order to get distinct values
    # print(fields)
    # fields = CleansingRule.query.filter_by(entity_id=entity_id).

    # prep entity valdiation dict
    entity_validation = {}

    # build validation dict for every field
    for f in fields:
        field = EntityField.query.get(str(f))  # convert to str or else you get errors
        dic = {}

        field_rules = rules_df[rules_df['entity_field_id'] == f]

        for i, r in field_rules.iterrows():
            rule = r['rule']
            criteria = r['criteria']

            # convert text values to int if possible
            try:
                criteria = int(criteria)
            except TypeError:
                pass
            except ValueError:
                pass

            # set true/false criteria
            if str(criteria) == 'False':
                criteria = False
            if criteria == 'True':
                criteria = True

            row_dic = {rule: criteria}
            # print(row_dic)
            dic.update(row_dic)

        entity_validation[field.field] = row_dic
        # entity_validation.append(validation_dict)

    # print(entity_validation)

    # store validation dict
    entity = Entity.query.get(entity_id)
    entity.data_cleansing_json = json.dumps(entity_validation)
    db.session.commit()


def generate_cerberus_data_issues(entity_id):
    # fetch entity & rules
    entity = Entity.query.get(entity_id)
    rules = CleansingRule.query.filter_by(entity_id=entity_id)
    # rules_df = pd.read_sql(rules.statement, rules.session.bind)

    # fetch loadfile
    df = get_loadfile(entity_id, validated=False)
    validation_dict = json.loads(entity.data_cleansing_json)
    # print(validation_dict)

    v = Validator(validation_dict)
    v.allow_unknown = True

    # convert df to dict for validation
    dic = df.to_dict(orient='records')

    issues = pd.DataFrame(columns=['customer_id', 'golive', 'code', 'rule_id', 'entity', 'field', 'issue', 'value'])
    for item in dic:
        if not v.validate(item):
            # get errors from cerberus
            error_df = pd.DataFrame.from_dict(v.errors, orient='index')
            error_df = error_df.reset_index(level=0)  # get indexes as columns

            # put all errors in global dataframe
            field = error_df['index'][0]
            issue_desc = error_df[0][0]

            issue = pd.DataFrame({'customer_id': entity.golive.customer_id,
                                  'golive': entity.golive_id,
                                    'code': item[entity.code_column],
                                    'rule_id': None,
                                    'entity': entity.entity,
                                    'field': field,
                                    'issue': issue_desc,
                                    'value': item[field]
                                  }, index=[0])
            issues = pd.concat([issues, issue])

    conn = config.sql_connect(db=entity.golive.customer.database_name)
    conn = conn.connect()
    print(issues)
    with conn:
        issues.to_sql('data_issues', conn, schema='reporting', if_exists='append', index=False)


def generate_pandas_data_issues(entity_id):
    issues = pd.DataFrame(columns=['code', 'rule_id', 'golive', 'entity', 'field', 'issue', 'value'])
    rules = CleansingRule.query.filter(and_(CleansingRule.entity_id == entity_id, CleansingRule.type == 'pandas'
                                            , CleansingRule.active == 'True'))

    loadfile = get_loadfile(entity_id, validated=False)

    for r in rules:
        field = EntityField.query.filter_by(id=r.entity_field).first()
        entity = Entity.query.filter_by(id=field.entity_id).first()

        issue = pd.DataFrame(columns=['code', 'issue', 'value'])

        df_filtered = loadfile.query(r.rule, engine='python')[[field.field]]
        issue['code'] = ''
        issue['golive'] = entity.golive_id
        issue['entity'] = entity.entity
        issue['field'] = field.field
        issue['issue'] = r.description
        issue['value'] = df_filtered[field.field]
        issue['rule_id'] = r.id

        # df_filtered = df_filtered.rename(columns={field: "value"})

        issues = issues.append(issue)

    print(issues)
    #issues.to_csv('test.csv', index=False)

    return issues


def get_cleansing_issues_count():
        database = current_user.customer.database_name

        conn = config.sql_connect(database)
        conn = conn.connect()

        count = pd.read_sql('select count(0) from reporting.data_issues where customer_id = \''
                            + current_user.customer_id + '\'', conn).iloc[0][0]
        print(count)

        return count

