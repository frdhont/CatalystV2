from app import db
from catalyst.reporting.data_cleaning import create_cerberus_validation_dict, generate_cerberus_data_issues, generate_data_issues
from catalyst.loadfiles.source_data import get_source_data
import config
import pandas as pd
from cerberus import Validator
import json
from catalyst.loadfiles import get_loadfile
from catalyst.models import Entity, ParameterQuery, GoLive, NumberSequence, EntityField
from catalyst.loadfiles import create
from app import db
import pytest
import numpy as np
#from pytest import TestC
from catalyst import create_task, process_all_tasks
from catalyst.loadfiles import mapping
from datetime import datetime
from msal import PublicClientApplication
create('BC01')
# ent = Entity.query.get(48)
# df = get_source_data(ent)
# mapping.map_entity(ent)
source_field = 'country'
# print(df)
# df = s.to_frame()
"""
prefix = 'lambda x:'
lam = '\'Belgium\' if x is None else x'
lam = prefix + lam
try:
    print(eval(lam))
    df['TEST'] = df[source_field].apply(eval(lam))
    # print(s)
except SyntaxError as e:
    print('invalid lambda syntax')
    pass




# print(df)
"""
"""
# x =
data = df.apply(lambda id: id + '0')

print(data)
"""