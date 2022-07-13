from catalyst.loadfiles import mapping, validate
import config
from datetime import datetime
from app import db
from catalyst.models import GoLive, Entity
import pandas as pd
from azure.storage.blob import BlobClient, BlobServiceClient
from pathlib import Path
import os
from sqlalchemy import and_


def create(gl):
    golive = GoLive.query.get(gl)

    if golive is None:
        print('Golive ' + gl + ' not found.')
        raise NameError('Golive ' + golive + ' not found')

    print('##### Creating all loadfiles for ' + golive.id)

    # fetch all entities for specified golive
    # print(golive.id)
    entities = Entity.query.filter(and_(Entity.golive_id == golive.id, Entity.active is True))

    # map all entities
    for entity in entities:
        # map entity
        loadfile = mapping.map_entity(entity)

        if loadfile is not None:

            # validate generated loadfile
            print('Validating loadfile')
            validated_lf = validate.validate_loadfile(loadfile, entity)
            print('Cleaning loadfile')
            cleaned_lf = validated_lf.query('validation_succesful == True').drop(['validation_succesful', 'errors'], axis='columns')

            conn = config.sql_connect(db=golive.customer.database_name)
            conn = conn.connect()

            with conn:
                print('Storing loadfiles in SQL DB')
                validated_lf.to_sql(entity.golive_id + '_' + entity.entity, conn, schema='loadfiles', if_exists='replace', index=False)
                cleaned_lf.to_sql(entity.golive_id + '_' + entity.entity, conn, schema='loadfiles_validated', if_exists='replace', index=False)

            # export loadfile
            export_loadfile(entity, cleaned_lf)

    golive.last_generated = datetime.now()
    db.session.commit()

    return


def get_loadfile(entity_id, validated=True):
    # fetch entity details
    entity = Entity.query.get(entity_id)
    database = entity.golive.customer.database_name

    conn = config.sql_connect(database)
    conn = conn.connect()

    with conn:
        if validated is True:
            df = pd.read_sql('select * from loadfiles_validated.' + entity.golive_id + '_' + entity.entity, conn)
        else:
            df = pd.read_sql('select * from loadfiles.' + entity.golive_id + '_' + entity.entity, conn)

        return df


def export_loadfile(entity, loadfile=None):
    # fetch loadfile if it's not provided
    if loadfile is None:
        loadfile = get_loadfile(entity.id)

    for exp in entity.export_details:

        export_target = exp.target

        if export_target == 'file':
            # init file export params
            path = entity.golive.customer_id + '/' + entity.golive_id + '/' + datetime.today().strftime('%Y%m%d')

            path = Path(path)
            path.mkdir(parents=True, exist_ok=True)

            export_type = exp.type

            if export_type == 'excel':

                # filepath = os.path.join(path + entity.entity, '.xlsx')
                file = entity.entity + '.xlsx'
                filepath = path / file
                loadfile.to_excel(filepath, index=False)

            elif export_type == 'csv':

                file = entity.entity + '.csv'
                filepath = path / file
                loadfile.to_csv(filepath, index=False)

            elif export_type == 'json':

                file = entity.entity + '.json'
                filepath = path / file
                loadfile.to_json(filepath, orient='records')

            elif export_type == 'xml':

                file = entity.entity + '.xml'
                filepath = path / file
                loadfile.to_xml(filepath, index=False)

            if file is not None:
                # export to fileshare
                service_client = BlobServiceClient.from_connection_string(os.getenv('EXPORT_BLOB_CONN_STRING'))
                container_client = service_client.get_container_client(os.getenv('EXPORT_BLOB_CONTAINER'))

                azure_path = os.path.join(path, file)
                blob_client = container_client.get_blob_client(azure_path)

                with open(filepath, "rb") as source_file:
                    blob_client.upload_blob(source_file, overwrite=True)  # overwrite if file already exists

                print('Entity ' + entity.entity + ' exported to ' + str(filepath))
        else:
            print()
            raise(ValueError('Export target ' + export_target + ' not supported'))