import pyodbc

driver= '{ODBC Driver 17 for SQL Server}'


def test_connection(server, database, username, password):
    try:
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            return True
    except:
        return False


def connect(server, database, username, password):
    try:
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            return conn
    except:
        return False


def execute_query(conn, query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor

