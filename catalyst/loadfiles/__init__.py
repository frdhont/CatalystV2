from catalyst.models import GoLive, Entity
from catalyst.loadfiles import mapping, validate
import pandas as pd
import config


def create(gl):
    golive = GoLive.query.get(gl)

    if golive is None:
        print('Golive ' + gl + ' not found.')
        return

    print('##### Creating all loadfiles for ' + golive.id)

    # fetch all entities for specified golive
    entities = Entity.query.filter_by(golive=golive.id)

    # map all entities
    for entity in entities:
        # map entity
        loadfile = mapping.map_entity(entity)

        # validate generated loadfile
        validated_lf = validate.validate_loadfile(loadfile, entity)
        cleaned_lf = validated_lf.query('validation_succesful == True').drop(['validation_succesful', 'errors'], axis='columns')

        conn = config.sql_connect(db=golive.database_name)
        conn = conn.connect()

        with conn:
            validated_lf.to_sql(entity.entity, conn, schema='loadfiles', if_exists='replace', index=False)
            cleaned_lf.to_sql(entity.entity, conn, schema='loadfiles_validated', if_exists='replace', index=False)

    return

