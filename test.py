from app import db
from catalyst.reporting.data_cleaning import create_cerberus_validation_dict, generate_cerberus_data_issues, generate_data_issues
from catalyst.loadfiles.source_data import get_source_data
import config
import pandas as pd
from cerberus import Validator
import json
from catalyst.loadfiles import get_loadfile
from catalyst.models import Entity, ParameterQuery, GoLive
from app import db
import pytest
import numpy as np
#from pytest import TestC
from catalyst import create_task, process_all_tasks
from catalyst.loadfiles import mapping
from datetime import datetime
from msal import PublicClientApplication
prefix = 'C'
start = 11000000
num = 100
s = pd.Series(np.arange(start=start, stop=start+num))
s = prefix + s
print(s)

"""
# x =
data = df.apply(lambda id: id + '0')

print(data)
"""