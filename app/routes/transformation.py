from flask import render_template, request
from app import app, db
from app.forms import EntityForm, GoLiveForm, EntityFieldForm
from catalyst import create_task
from catalyst.models import Entity, GoLive, Translation, EntityField, NumberSequence, Parameter
from flask_login import current_user, login_required
import sqlalchemy.exc
from sqlalchemy.exc import ProgrammingError, IntegrityError
import config
import pandas as pd
import re


@app.route('/transformation/entities', methods=['GET', 'POST'])
@login_required
def entities():

    toggle_activate = request.args.get('toggle_activate')
    if toggle_activate:
        entity = Entity.query.get(toggle_activate)
        entity.toggle_activate
        print('Entity toggle activate')

    # fetch allowed golives for user
    # golives = GoLive.query.filter_by(customer_id=current_user.customer_id)
    # allowed_golives = [gl.id for gl in golives]
    allowed_golives = current_user.allowed_golives
    golive_choices = [(gl, gl) for gl in allowed_golives]

    # init form + set go live choices to allowed values
    form = EntityForm()
    form.golive.choices = golive_choices

    if form.validate_on_submit():

        entity = Entity(golive_id=form.golive.data, entity=form.entity.data, description=form.description.data,
                        target_system=form.target_system.data, source_view=form.source_view.data
                        , entity_group=form.group.data
                        # scope_column=form.scope_column.data
                        )

        try:
            db.session.add(entity)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            error_message = 'Entity \'' + entity.entity + '\' already exists for go-live ' + entity.golive_id

    entities = Entity.query.filter(Entity.golive_id.in_(allowed_golives)).order_by(Entity.golive_id, Entity.entity).all()

    return render_template('transformation/entities.html', nbar='transformation', **locals())


@app.route('/transformation/entities/<entity_id>/edit', methods=['GET', 'POST'])
@login_required
def entities_edit(entity_id):
    entity = Entity.query.get(entity_id)
    #print(entity.allow_unknown)

    form = EntityForm()

    # fill edit form
    form.golive.choices = [(entity.golive_id, entity.golive_id)]
    form.golive.data = entity.golive_id
    form.entity.data = entity.entity
    form.validation_json.data = entity.validation_json
    form.description.data = entity.description

    if request.method == 'POST':
        if form.validate_on_submit():
            updated_entity = Entity.query.get(entity.id)
            updated_entity.description = form.description.data
            updated_entity.target_system = form.target_system.data
            updated_entity.source_view = form.source_view.data
            updated_entity.scope_column = form.scope_column.data
            updated_entity.allow_unknown = form.allow_unknown.data

            # db.session.add(entity)
            db.session.commit()
        else:
            print(form.errors)

    return render_template('transformation/entity_edit.html', nbar='transformation', **locals())


@app.route('/transformation/entities/<entity_id>/fields', methods=['GET', 'POST'])
@login_required
def entities_fields(entity_id):
    entity = Entity.query.get(entity_id)

    if entity is not None:
        # delete if requested
        if request.args.get('delete'):
            delete = request.args.get('delete')
            try:
                EntityField.query.filter_by(id=delete).delete(synchronize_session='fetch')
                db.session.commit()
            except IntegrityError as e:
                error_message = 'Can\'t delete field, linked object exists'
                db.session.rollback()

        # fetch all field data
        fields = EntityField.query.filter_by(entity_id=entity.id)

        # init form
        form = EntityFieldForm()

        # fetch all form choices and pass to form
        translation_types = db.session.query(Translation.translation_key).filter_by(customer_id=current_user.customer_id).distinct()
        form.translation_key.choices = [('', '')] + [(tl.translation_key, tl.translation_key) for tl in translation_types]

        num_seq = NumberSequence.query.filter_by(customer_id=current_user.customer_id)
        form.number_sequence.choices = [('', '')] + [(n.id, n.name) for n in num_seq]

        parameters = db.session.query(Parameter.parameter).filter_by(
            customer_id=current_user.customer_id).distinct()
        form.parameter.choices = [('', '')] + [(tl.parameter, tl.parameter) for tl in parameters]

        if request.method == 'POST':
            if form.regex_validation.data:
                try:
                    re.compile(form.regex_validation.data)
                except re.error:
                    error_message = form.regex_validation.data + ' is not a valid regex format'
                    return render_template('transformation/entity_fields.html', nbar='configuration', **locals())

            if form.validate_on_submit():
                # print(form.number_sequence.data)
                #print(form.translation_key.data.type)

                field = EntityField(entity_id=entity_id, field=form.field.data, precision=form.precision.data,
                                    allow_null=form.allow_null.data, description=form.description.data,
                                    mapping_type=form.mapping_type.data, default_value=form.default.data,
                                    parameter=form.parameter.data,
                                    number_sequence_id=form.number_sequence.data,
                                    source_field=form.source_field.data, translation_key=form.translation_key.data,
                                    regex_validation=form.regex_validation.data, type=form.type.data,
                                    transformation_rule=form.transformation.data, golive_id=entity.golive_id)


                try:
                    db.session.add(field)
                    db.session.commit()
                except IntegrityError as e:
                    db.session.rollback()
                    error_message = 'Field ' + field.field + ' already exists for entity ' + entity.entity
                    return render_template('transformation/entity_fields.html', nbar='configuration', **locals())

            else:
                print(form.errors)

    return render_template('transformation/entity_fields.html', nbar='transformation', **locals())


@app.route('/transformation/entities/fields/<field_id>', methods=['GET', 'POST'])
@login_required
def entities_field_edit(field_id):
    field = EntityField.query.get(field_id)

    if field is not None:
        # init form
        form = EntityFieldForm()

        # fetch all form choices and pass to form
        translation_types = db.session.query(Translation.translation_key).distinct()
        translation_choices = [('', '')] + [(tl.translation_key, tl.translation_key) for tl in translation_types]
        form.translation_key.choices = translation_choices

        num_seq = db.session.query(NumberSequence.id, NumberSequence.name).distinct()
        num_seq = [('', '')] + [(n.id, n.name) for n in num_seq]
        form.number_sequence.choices = num_seq

        parameters = db.session.query(Parameter.parameter).filter_by(
            customer_id=current_user.customer_id).distinct()
        form.parameter.choices = [('', '')] + [(tl.parameter, tl.parameter) for tl in parameters]

        if request.method == 'POST':
            form.field.data = field.field
            if form.validate_on_submit():
                # print(form.number_sequence.data)
                #print(form.translation_key.data.type)

                field.precision = form.precision.data
                field.allow_null = form.allow_null.data
                field.description = form.description.data
                field.mapping_type = form.mapping_type.data
                default_value = form.default.data
                field.parameter = form.parameter.data
                field.number_sequence_id = form.number_sequence.data
                field.source_field = form.source_field.data
                field.translation_key = form.translation_key.data
                field.transformation_rule = form.transformation.data
                field.regex_validation = form.regex_validation.data
                field.type = form.type.data

                db.session.commit()

                return render_template('transformation/entity_field_edit.html', nbar='configuration', **locals())

            else:
                print(form.errors)
                error_message = form.errors

    return render_template('transformation/entity_field_edit.html', nbar='transformation', **locals())


@app.route('/transformation/entities/preview/<entity_id>')
@login_required
def entities_preview(entity_id):
    entity = Entity.query.get(entity_id)
    golive = GoLive.query.get(entity.golive_id)

    if entity is not None:
        sql = 'select top 100 * from ' + golive.customer.database_name + '.loadfiles.' + entity.golive_id + '_' + entity.entity

        conn = config.sql_connect(db=golive.customer.database_name)
        conn = conn.connect()

        with conn:
            try:
                loadfile = pd.read_sql(sql, conn)
                column_names = loadfile.columns.values
                row_data = list(loadfile.values.tolist())
            except ProgrammingError:
                does_not_exist = True

    return render_template('transformation/entity_preview.html', nbar='transformation', **locals(), zip=zip)


@app.route('/transformation/golives', methods=['GET', 'POST'])
@login_required
def golives():

    regenerate_data = request.args.get('regenerate_data')
    if regenerate_data:
        create_task('create_loadfiles', regenerate_data)

    clone = request.args.get('clone')
    if clone:
        create_task('clone_golive', clone)

    toggle_activate = request.args.get('toggle_activate')
    if toggle_activate:
        gl = GoLive.query.get(toggle_activate)
        gl.toggle_activate

    form = GoLiveForm()

    if form.validate_on_submit():
        golive = GoLive(id=form.golive.data, name=form.name.data,
                        customer_id=current_user.customer_id, go_live_date=form.go_live_date.data)
        db.session.add(golive)
        db.session.commit()

    golives = GoLive.query.filter_by(customer_id=current_user.customer_id)

    return render_template('transformation/golives.html', nbar='transformation', **locals())

