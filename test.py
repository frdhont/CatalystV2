from app import db
from catalyst.reporting import data_cleaning
from catalyst.models import CleansingRule
from sqlalchemy import and_

data_cleaning.generate_data_issues('MO01')