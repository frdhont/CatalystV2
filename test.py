from app import db
from catalyst.data_cleaning import create_cerberus_validation_dict, generate_cerberus_data_issues
import config
import pandas as pd
from cerberus import Validator
import json
from catalyst.loadfiles import get_loadfile

get_loadfile(2)




# create_cerberus_validation_dict(2)
generate_cerberus_data_issues(2)



# df = pd.read_sql('select [rule], criteria from cleansing_rules', conn)
#print(df)


