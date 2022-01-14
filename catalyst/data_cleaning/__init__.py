import pandas as pd
import config
from catalyst.models import CleansingRule, Entity, EntityField, Customer, GoLive


def generate_data_issues(customer):
    # fetch all cleansing rules for the selected customer
    golives = GoLive.query.filter_by(customer_id=customer)
    golives = [gl.id for gl in golives]

    entities = Entity.query.filter(Entity.golive.in_(golives))
    entities = [e.id for e in entities]

    fields = EntityField.query.filter(EntityField.entity_id.in_(entities))
    fields = [f.id for f in fields]

    rules = CleansingRule.query.filter(CleansingRule.entity_field.in_(fields))

    customer = Customer.query.filter_by(id=customer).first()

    issues = pd.DataFrame(columns=['code', 'rule_id', 'golive', 'entity', 'field', 'issue', 'value'])

    for r in rules:
        field = EntityField.query.filter_by(id=r.entity_field).first()
        entity = Entity.query.filter_by(id=field.entity_id).first()

        conn = config.sql_connect('mock_db')
        conn = conn.connect()

        with conn:
            df = pd.read_sql('select * from loadfiles.' + entity.golive + '_' + entity.entity_id, conn)
            # print(df)

        issue = pd.DataFrame(columns=['code', 'issue', 'value'])

        df_filtered = df.query(r.rule, engine='python')[[field.field]]
        issue['value'] = df_filtered[field.field]
        issue['issue'] = r.description
        issue['rule_id'] = r.id
        issue['entity'] = entity.entity_id
        issue['field'] = field.field
        issue['golive'] = entity.golive
        # df_filtered = df_filtered.rename(columns={field: "value"})

        issues = issues.append(issue)

    issues.to_csv('test.csv', index=False)

    conn = config.sql_connect(customer.database_name)
    conn = conn.connect()

    with conn:
        issues.to_sql('data_cleaning_issues', conn, if_exists='replace', index=False, schema='reporting')