from app import db
from catalyst.reporting import data_cleaning
from catalyst.models import CleansingRule, Entity
from sqlalchemy import and_
from catalyst.loadfiles import create, source_data
import catalyst

# create('POC')
data_cleaning.generate_data_issues('POC')