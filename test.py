from app import db
from catalyst.reporting.data_cleaning import create_cerberus_validation_dict, generate_cerberus_data_issues, generate_data_issues
import config
import pandas as pd
from cerberus import Validator
import json
from catalyst.loadfiles import get_loadfile

generate_data_issues('MO01')

# df = pd.read_sql('select [rule], criteria from cleansing_rules', conn)
#print(df)
