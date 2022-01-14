from flask import render_template, request
from app import app, db
from app.forms import CleansingForm
from catalyst import create_task
from catalyst.models import Entity, GoLive, Translation, EntityField, CleansingRule
from flask_login import login_required
from sqlalchemy.exc import IntegrityError, ProgrammingError
import config
import pandas as pd


@app.route('/validation/cleansing_rules', methods=['GET', 'POST'])
@login_required
def cleansing_rules():

    cleansing_rules = CleansingRule.query.all()

    for c in cleansing_rules:
        print(c.entity_field)

    form = CleansingForm

    return render_template('validation/cleansing_rules.html', nbar='validation', **locals())

