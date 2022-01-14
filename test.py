from app import db
from catalyst import process_all_tasks
from catalyst.loadfiles import create
import pandas as pd
import config
from catalyst.loadfiles.validate import create_validation_dict
from catalyst.models import UserRoles, Role, User, Task, CleansingRule, Entity, EntityField
from catalyst.reporting import generate_migration_dashboard, get_migration_dashboard
from catalyst.data_cleaning import generate_data_issues

cleansing_rules = CleansingRule.query.all()

for c in cleansing_rules:
    print(c.entity_field.entity.golive)