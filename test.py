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
#from pytest import TestC

entity = GoLive.query.get('MO01')
e = entity.clone(new_golive='CO01')
print(e)
"""
# x =
data = df.apply(lambda id: id + '0')

print(data)
"""