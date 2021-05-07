from dataclasses import dataclass
import os
import urllib.parse
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

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

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('CATALYST_SQL_DB_URI')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)

from app import routes
