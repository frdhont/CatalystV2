from app import db
from catalyst.reporting import data_cleaning
from catalyst.models import CleansingRule, Entity
from sqlalchemy import and_
from catalyst.loadfiles import create, source_data
import catalyst
import re

# pattern is a string containing the regex pattern
pattern = "[.*"

try:
    re.compile(pattern)

except re.error:
    print("Non valid regex pattern")
    exit()