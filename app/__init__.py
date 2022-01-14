from dataclasses import dataclass
import os
import urllib.parse
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_user import UserManager
from flask_login import LoginManager

# load environment variables
load_dotenv()
"""
# Configure Database URI:
driver= '{ODBC Driver 17 for SQL Server}'
server = 'catalyst-migrator.database.windows.net'
catalyst_db = 'catalyst'
dwh_db = 'dwh'
user = 'frdho'
pw = 'qdKsQcW6Y6ePvgx'
params = urllib.parse.quote_plus('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+catalyst_db+';UID='+user+';PWD='+ pw)
"""

sql_host = os.getenv('CATALYST_SQL_DB_URL')
sql_db = os.getenv('CATALYST_SQL_DB')
user = os.getenv('CATALYST_SQL_DB_USER')
pw = os.getenv('CATALYST_SQL_DB_PW')
uri = "mssql+pyodbc:///?odbc_connect={}".format(urllib.parse.quote_plus(
            "DRIVER=ODBC Driver 17 for SQL Server;SERVER={0};PORT=1433;DATABASE={1};UID={2};PWD={3};TDS_Version=8.0;".format(
                sql_host, sql_db, user, pw))) #os.getenv('CATALYST_SQL_DB_URI')

# initialization
app = Flask(__name__, static_url_path='/app/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = uri

app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True  # enable debugging
app.config['USER_EMAIL_SENDER_EMAIL'] = 'frdhont@gmail.com'  # enable debugging

# login config
login = LoginManager()
login.init_app(app)
login.login_view = 'login'


# extensions
db = SQLAlchemy(app)


# Setup Flask-User
# user_manager = UserManager(app, db, User)
# user_manager.login_manager = login


#user_manager.login_manager = login

from app.routes import index, auth, admin, tasks
from app.routes import transformation, validation



