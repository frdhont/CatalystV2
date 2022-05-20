from flask import render_template, request
from app import app, db
from app.forms import CleansingForm
from catalyst import create_task
from catalyst.models import Customer, CleansingRule, GoLive
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError, ProgrammingError
import config
import pandas as pd


@app.route('/validation/cleansing_rules', methods=['GET', 'POST'])
@login_required
def cleansing_rules():

    cleansing_rules = CleansingRule.query.all()

    form = CleansingForm

    return render_template('validation/cleansing_rules.html', nbar='validation', **locals())


@app.route('/validation/data_issues/', methods=['GET', 'POST'])
@login_required
def validation_data_issues():

    # check if data issues need to be regenerated
    generate_issues = request.args.get('generate_issues')
    if generate_issues:
        create_task('generate_data_issues', generate_issues)

    golives = GoLive.query.filter_by(customer_id=current_user.customer)

    return render_template('validation/data_issues.html', nbar='validation', **locals())


@app.route('/validation/data_issues/<golive>', methods=['GET', 'POST'])
@login_required
def validation_data_issues_detail(golive):

    golive = GoLive.query.filter_by(id=golive).first()

    if golive is not None:
        sql = 'select * from reporting.' + golive.id + '_DataIssues'

        conn = config.sql_connect(db=golive.customer.database_name)
        conn = conn.connect()

        with conn:
            try:
                data_issues = pd.read_sql(sql, conn)
                print(data_issues)
                column_names = data_issues.columns.values
                row_data = list(data_issues.values.tolist())
            except ProgrammingError:
                does_not_exist = True

    return render_template('validation/data_issues_detail.html', nbar='validation', **locals(), zip=zip)
