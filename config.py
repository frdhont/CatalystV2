import os
import urllib
from sqlalchemy import create_engine
from dotenv import load_dotenv

# load environment variables
load_dotenv()


def sql_connect(db=None):
    sql_host = os.getenv('CATALYST_SQL_DB_URL')
    user = os.getenv('CATALYST_SQL_DB_USER')
    pw = os.getenv('CATALYST_SQL_DB_PW')

    if db is None:
        sql_db = os.getenv('CATALYST_SQL_DB')
    else:
        sql_db = db

    #uri = os.getenv('CATALYST_SQL_DB_URI')
    try:
        # conn = create_engine(uri, fast_executemany=True, pool_pre_ping=True)
        uri = "mssql+pyodbc:///?odbc_connect={}".format(urllib.parse.quote_plus(
            "DRIVER=ODBC Driver 17 for SQL Server;SERVER={0};PORT=1433;DATABASE={1};UID={2};PWD={3};TDS_Version=8.0;".format(
                sql_host, sql_db, user, pw)))
        conn = create_engine(uri, fast_executemany=True, pool_pre_ping=True)
        # print('Succesfully connected to SQL DB')
        return conn
    except Exception as e:
        print('SQL Connection failed! Error:')
        print(e)
        return False