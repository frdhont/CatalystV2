from catalyst.models import GoLive, Entity, Customer
import config
import pandas as pd
from sqlalchemy.exc import ProgrammingError


def generate_migration_dashboard(customer_id):
    customer = Customer.query.get(customer_id)
    database = customer.database_name
    golives = GoLive.query.filter_by(customer_id=customer_id)

    golive = []
    entity = []
    legacy_count = []
    in_scope = []
    loadfile = []
    issues = []
    cleansing = []

    for gl in golives:

        entities = Entity.query.filter_by(golive_id=gl.id).all()

        conn = config.sql_connect(db=database)
        conn = conn.connect()

        with conn:
            for ent in entities:

                golive.append(ent.golive_id)
                entity.append(ent.entity)

                try:
                    sql = 'select count(0) count from ' + ent.source_view
                    df = pd.read_sql(sql, conn)
                    legacy_count.append(df['count'].iloc[0])
                except ProgrammingError:
                    legacy_count.append(0)
                try:
                    sql = 'select count(0) count from ' + ent.source_view + ' where ' + ent.scope_column + ' = 1'
                    df = pd.read_sql(sql, conn)
                    in_scope.append(df['count'].iloc[0])
                except ProgrammingError:
                    in_scope.append(0)

                try:
                    sql = 'select count(0) count from loadfiles.' + ent.golive_id + '_' + ent.entity + \
                          ' where validation_succesful = 1'
                    df = pd.read_sql(sql, conn)
                    loadfile.append(df['count'].iloc[0])
                except ProgrammingError:
                    loadfile.append(0)

                try:
                    sql = 'select count(0) count from loadfiles.' + ent.golive_id + '_' + ent.entity + \
                          ' where validation_succesful = 0'
                    df = pd.read_sql(sql, conn)
                    issues.append(df['count'].iloc[0])
                except ProgrammingError:
                    issues.append(0)


    # init dataframe
    db = pd.DataFrame()

    db['golive'] = golive
    db['entity'] = entity
    db['legacy_count'] = legacy_count
    db['in_scope'] = in_scope
    db['loadfile'] = loadfile
    db['issues'] = issues
    # db['cleansing'] = cleansing
    db['customer'] = str(customer_id)

    print(db)

    conn = config.sql_connect(db=database)
    conn = conn.connect()

    with conn:

        db.to_sql('migration_dashboard', conn, schema='reporting', if_exists='replace', index=False)

    print('Migration dashboard generated')
    return db


def get_migration_dashboard(customer_id):
    customer = Customer.query.get(customer_id)
    database = customer.database_name

    conn = config.sql_connect(db=database)
    conn = conn.connect()

    with conn:
        try:
            dashboard = pd.read_sql('select * from reporting.migration_dashboard where customer = \''
                                + customer_id + '\'', conn)
        except ProgrammingError:
            return

    # prepare chart data

    dashboard['labels'] = dashboard['golive'] + ' - ' + dashboard['entity']
    labels = dashboard['labels'].to_list()
    legacy_values = dashboard['legacy_count'].to_list()
    scope_values = dashboard['in_scope'].to_list()
    loadfile_values = dashboard['loadfile'].to_list()
    issues_values = dashboard['issues'].to_list()

    #drop unnecessary columns
    dashboard.drop(['customer', 'golive', 'entity'], inplace=True, axis=1)

    print(dashboard)

    return dashboard, labels, legacy_values, scope_values, loadfile_values, issues_values