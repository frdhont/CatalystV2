from flask import render_template, request
from app import app, db
from app.forms import CleansingForm
from catalyst import create_task
from catalyst.models import Customer, CleansingRule, GoLive, Entity, EntityField
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError, ProgrammingError
import config
import pandas as pd


@app.route('/validation/cleansing_rules', methods=['GET', 'POST'])
@login_required
def cleansing_rules():
    # delete if requested
    if request.args.get('delete'):
        delete = request.args.get('delete')
        CleansingRule.query.filter_by(id=delete).delete(synchronize_session='fetch')
        db.session.commit()
    # init form & set allowed values
    form = CleansingForm()

    # allowed golives
    allowed_golives = current_user.allowed_golives
    # form.golive.choices = [(gl, gl) for gl in allowed_golives]

    # allowed entities
    # TODO: set allowed entities based on golive choice?
    entities = Entity.query.filter(Entity.golive_id.in_(allowed_golives)).order_by(Entity.golive_id,
                                                                                   Entity.entity).all()
    allowed_entities = [e.id for e in entities]
    # form.entity.choices = [(e.id, e.golive_id + ' - ' + e.entity) for e in entities]

    # allowed fields
    # TODO: set allowed fields based on entity choice?
    fields = EntityField.query.filter(EntityField.entity_id.in_(allowed_entities)).all()
    form.field.choices = [(f.id, f.entity.golive_id + ' - ' + f.entity.entity + ' - ' + f.field) for f in fields]

    if form.validate_on_submit():
        field = EntityField.query.get(form.field.data)

        rule = CleansingRule(entity_id=field.entity_id, golive_id=field.entity.golive_id, entity_field_id=form.field.data
                             , description=form.description.data, type=form.type.data
                             , rule=form.rule.data, criteria=form.criteria.data)

        try:
            db.session.add(rule)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()


    cleansing_rules = CleansingRule.query.all()
    cleansing_rules = db.session.query(CleansingRule).join(GoLive).filter(GoLive.customer_id == current_user.customer_id)



    return render_template('validation/cleansing_rules.html', nbar='validation', **locals())


@app.route('/validation/data_issues/', methods=['GET', 'POST'])
@login_required
def validation_data_issues():

    # check if data issues need to be regenerated
    generate_issues = request.args.get('generate_issues')
    if generate_issues:
        create_task('generate_data_issues', generate_issues)

    golives = GoLive.query.filter_by(customer_id=current_user.customer_id)


    sql = 'select * from reporting.data_issues'
    database = current_user.customer.database_name

    conn = config.sql_connect(database)
    with conn.connect():
        df = pd.read_sql(sql, conn)

    print(df)
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
                column_names = data_issues.columns.values
                row_data = list(data_issues.values.tolist())
            except ProgrammingError:
                does_not_exist = True

    return render_template('validation/data_issues_detail.html', nbar='validation', **locals(), zip=zip)
