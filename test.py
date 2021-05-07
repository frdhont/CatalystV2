from app import db
from catalyst.loadfiles import create
import pandas as pd
import config
from catalyst.loadfiles.validate import create_validation_dict

create_validation_dict(1)

create('MO01')
# db.create_all()