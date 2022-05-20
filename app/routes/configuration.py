from flask import render_template, request
from app import app, db
from app.forms import TranslationForm, NumberSequenceForm, ParameterForm
from catalyst.models import Entity, GoLive, Translation,  NumberSequence, Parameter
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError


@app.route('/configuration/translations', methods=['GET', 'POST'])
@login_required
def configuration_translations():
    # fetch allowed golives for user
    golives = GoLive.query.filter_by(customer_id=current_user.customer)
    allowed_golives = [gl.id for gl in golives]
    golive_choices = [(gl.id, gl.id) for gl in golives]

    # init form + set go live choices to allowed values
    form = TranslationForm()
    form.golive.choices = golive_choices

    if form.validate_on_submit():
        translation = Translation(golive=form.golive.data, translation_key=form.translation_key.data,
                                  from_value=form.from_value.data, to_value=form.to_value.data)
        db.session.add(translation)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            already_exists = True

    translations = Translation.query.all()

    return render_template('configuration/translations.html', nbar='configuration', **locals())


@app.route('/configuration/parameters', methods=['GET', 'POST'])
@login_required
def configuration_parameters():
    parameters = Parameter.query.all()

    # fetch golives
    golives = GoLive.query.filter_by(customer_id=current_user.customer)
    golive_choices = [('', '')] + [(gl.id, gl.id) for gl in golives]

    # init form
    form = ParameterForm()
    form.golive.choices = golive_choices

    if request.method == 'POST':
        if form.validate_on_submit():

            parameter = Parameter(parameter=form.parameter.data, value=form.value.data,
                                      golive_id=form.golive.data, customer_id=current_user.customer)

            try:
                db.session.add(parameter)
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                error_message = 'Parameter ' + parameter.parameter + ' already exists for golive ' + parameter.golive_id
                return render_template('configuration/parameters.html', nbar='configuration', **locals())

            parameters = Parameter.query.all()
        else:
            print(form.errors)

    return render_template('configuration/parameters.html', nbar='configuration', **locals())


@app.route('/configuration/number_sequences', methods=['GET', 'POST'])
@login_required
def configuration_sequences():
    # sequences = NumberSequence.query.filter_by(customer_id=current_user.customer)
    sequences = NumberSequence.query.all()

    # generate example number
    for s in sequences:
        s.example = s.prefix + str(s.start).zfill(s.length)

    print(sequences)
    # init form
    form = NumberSequenceForm()

    if request.method == 'POST':
        if form.validate_on_submit():

            sequence = NumberSequence(name=form.name.data, prefix=form.prefix.data, start=form.start.data
                                      , length=form.length.data, customer_id=current_user.customer)
            db.session.add(sequence)
            db.session.commit()

            sequences = NumberSequence.query.all()
        else:
            print(form.errors)

    return render_template('configuration/number_sequences.html', nbar='configuration', **locals())
