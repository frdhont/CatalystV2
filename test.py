from app import db
from catalyst.reporting import data_cleaning
from catalyst.models import CleansingRule, Entity
from sqlalchemy import and_
from catalyst.loadfiles import create, source_data
import catalyst

entity = Entity.query.get(2)
df = source_data.get_source_data(entity)