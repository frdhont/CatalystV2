from catalyst.models import GoLive
import pandas as pd
import config


def get_source_data(entity):
    # golive = GoLive.query.get(entity.golive_id)
    db = entity.golive.customer.database_name

    conn = config.sql_connect(db)
    conn = conn.connect()

    with conn:
        df = pd.read_sql('select * from ' + entity.source_view, conn)

    return df
