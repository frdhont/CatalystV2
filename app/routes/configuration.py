from flask import render_template, request
from app import app, db
from app.forms import TranslationForm, NumberSequenceForm, ParameterForm
from catalyst.models import Entity, GoLive, Translation,  NumberSequence, Parameter, EntityField
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_


@app.route('/configuration/translations', methods=['GET', 'POST'])
@login_required
def configuration_translations():
    if request.args.get('delete'):
        delete = request.args.get('delete')
        tl = Translation.query.get(delete)
        if tl.golive.customer_id == current_user.customer_id:
            Translation.query.filter_(Translation.id == delete).delete()
            db.session.commit()
        else:
            error_message = 'Translation not found'

    # fetch allowed golives for user
    golives = GoLive.query.filter_by(customer_id=current_user.customer_id)
    allowed_golives = [gl.id for gl in golives]
    golive_choices = [(gl.id, gl.id) for gl in golives]

    # init form + set go live choices to allowed values
    form = TranslationForm()
    form.golive.choices = golive_choices

    if form.validate_on_submit():
        translation = Translation(golive_id=form.golive.data, translation_key=form.translation_key.data,
                                  from_value=form.from_value.data, to_value=form.to_value.data)
        db.session.add(translation)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            error_message = 'A translation with following properties already exists: ' + form.golive.data + \
                            ', ' + form.translation_key.data + ', ' + form.from_value.data

    translations = db.session.query(Translation).join(GoLive).filter(GoLive.customer_id == current_user.customer_id)

    return render_template('configuration/translations.html', nbar='configuration', **locals())


@app.route('/configuration/parameters', methods=['GET', 'POST'])
@login_required
def configuration_parameters():
    # delete if requested
    if request.args.get('delete'):
        delete = request.args.get('delete')
        Parameter.query.filter(and_(Parameter.id == delete,
                                    Parameter.customer_id == current_user.customer_id)).delete(synchronize_session='fetch')
        db.session.commit()

    # fetch golives
    golives = GoLive.query.filter_by(customer_id=current_user.customer_id)
    golive_choices = [('', '')] + [(gl.id, gl.id) for gl in golives]

    # init form
    form = ParameterForm()
    form.golive.choices = golive_choices

    if request.method == 'POST':
        print(form.golive.data)
        if form.validate_on_submit():

            parameter = Parameter(parameter=form.parameter.data, value=form.value.data,
                                  golive_id=form.golive.data, customer_id=current_user.customer_id)

            try:
                db.session.add(parameter)
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                error_message = 'Parameter ' + parameter.parameter + ' already exists for golive ' + parameter.golive_id
                parameters = Parameter.query.filter_by(customer_id=current_user.customer_id)
                return render_template('configuration/parameters.html', nbar='configuration', **locals())

        else:
            error_message = form.errors

    parameters = Parameter.query.filter_by(customer_id=current_user.customer_id)

    return render_template('configuration/parameters.html', nbar='configuration', **locals())


@app.route('/configuration/number_sequences', methods=['GET', 'POST'])
@login_required
def configuration_sequences():
    if request.args.get('delete'):
        delete = request.args.get('delete')
        ent = EntityField.query.filter_by(number_sequence_id=delete).first()
        if ent:
            error_message = 'Number sequence in use, can\'t be deleted'
        else:
            NumberSequence.query.filter(and_(NumberSequence.id == delete,
                                             NumberSequence.customer_id == current_user.customer_id))\
                .delete(synchronize_session='fetch')
            db.session.commit()
            message = 'Number sequence deleted'


    # sequences = NumberSequence.query.all()

    # init form
    form = NumberSequenceForm()

    if request.method == 'POST':
        if form.validate_on_submit():

            sequence = NumberSequence(name=form.name.data, prefix=form.prefix.data, start=form.start.data
                                      , length=form.length.data, customer_id=current_user.customer_id)
            sequence.set_example()
            db.session.add(sequence)
            db.session.commit()

            message = 'Number sequence added'

        else:
            print(form.errors)

    sequences = NumberSequence.query.filter_by(customer_id=current_user.customer_id)

    return render_template('configuration/number_sequences.html', nbar='configuration', **locals())
