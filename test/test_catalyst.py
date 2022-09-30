from catalyst.models import Entity, ParameterQuery
from catalyst.loadfiles import create
from catalyst.loadfiles import validate
from catalyst.reporting import generate_migration_dashboard, get_migration_dashboard
from catalyst.reporting.data_cleaning import generate_data_issues

""""
def test_create():
    create('MO01')
"""


def test_param_empty_golive():
    param = ParameterQuery.get_parameter(parameter='SPOC', golive_id='MO01',customer_id='MOCK')
    print(param)

    assert param == 'Frederik Dhont'


def test_param_filled_golive():
    param = ParameterQuery.get_parameter(parameter='SPOC', golive_id='MO02',customer_id='MOCK')
    print(param)

    assert param == 'Vic Dhont'


def test_create_validation_dict():
    validate.create_validation_dict(2)


def test_generate_data_issues():
    generate_data_issues('MO01')


def test_generate_migration_dashboard():
    generate_migration_dashboard('MOCK')


def test_get_migration_dashboard():
    dashboard, labels, legacy_values, scope_values, loadfile_values, issues_values = get_migration_dashboard('MOCK')


def test_create_loadfiles():
    create('MO01')
