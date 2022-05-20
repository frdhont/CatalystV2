from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SelectField, TextAreaField, BooleanField, IntegerField
from wtforms.fields import EmailField, DateField
from wtforms.widgets import TextArea
from wtforms.validators import InputRequired, Optional

"""
# Custom validators
class RequiredIf(InputRequired):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)

        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)
"""

class RequiredIfFieldEqualTo(InputRequired):
    # a validator which makes a field optional if
    # another field has a desired value

    def __init__(self, other_field_name, value, *args, **kwargs):
        self.other_field_name = other_field_name
        self.value = value
        print('other_field_name: ' + other_field_name)
        print('value: ' + value)
        super(RequiredIfFieldEqualTo, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        # if other_field.data != self.value:
        #    print('Field not equal to ' + self.value)
        if other_field.data == self.value:
            print('Field equal to ' + self.value)
            super(RequiredIfFieldEqualTo, self).__call__(form, field)
#"""

class EntityForm(FlaskForm):
    golive = SelectField('Go live', validators=[validators.DataRequired()])
    entity = StringField('Entity', validators=[validators.DataRequired()])
    description = StringField('Description', filters=[lambda x: x or None], widget=TextArea())
    target_system = StringField('Target system')
    source_view = StringField('Source view', validators=[validators.DataRequired()])
    # scope_column = StringField('Scope column', validators=[validators.DataRequired()])
    validation_json = TextAreaField('Validation JSON', render_kw={"rows": 10, "cols": 11})
    allow_unknown = BooleanField('Allow unknown fields')


class EntityFieldForm(FlaskForm):
    field = StringField('Field', validators=[validators.DataRequired()])
    type = SelectField('Type', validators=[validators.DataRequired()], choices=[('string', 'String')
        , ('integer', 'Integer'), ('float', 'Float'), ('number', 'Number'), ('boolean', 'Boolean')
        , ('datetime', 'Datetime'), ('date', 'Date')])
    precision = StringField('Precision')
    description = StringField('Description', filters=[lambda x: x or None])
    allow_null = BooleanField('Allow empty')
    mapping_type = SelectField('Mapping type', validators=[validators.DataRequired()], choices=[('default', 'Default')
        , ('one_to_one', 'One to one'), ('translation', 'Translation'), ('parameter', 'Parameter')
        , ('number_sequence', 'Number sequence'), ('transformation', 'Transformation')])
    default = StringField('Default value', filters=[lambda x: x or None])  # lambda to insert NULL instead of "" to sql
    parameter = StringField('Parameter', filters=[lambda x: x or None])
    source_field = StringField('Source field', filters=[lambda x: x or None])
    translation_key = SelectField('Translation key', validators=[validators.Optional()], filters=[lambda x: x or None])
    regex_validation = StringField('Regex validation', filters=[lambda x: x or None])
    transformation = StringField('Transformation rule', filters=[lambda x: x or None])
    number_sequence = SelectField('Number sequence', validators=[validators.Optional()], filters=[lambda x: x or None])


class GoLiveForm(FlaskForm):
    golive = StringField('Go live', validators=[validators.DataRequired()])
    name = StringField('Name', validators=[validators.DataRequired()])
    go_live_date = DateField('Go-live date')
    database_name = StringField('Database name')


class TranslationForm(FlaskForm):
    golive = SelectField('Go live', validators=[validators.DataRequired()])
    translation_key = StringField('Translation key', validators=[validators.DataRequired()])
    from_value = StringField('From value', validators=[validators.DataRequired()])
    to_value = StringField('To value', validators=[validators.DataRequired()])


class LoginForm(FlaskForm):
    #general
    email = EmailField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])


class SignupForm(FlaskForm):

    email = EmailField('Email', [validators.DataRequired(), validators.Email()])
    first_name = StringField('First name', [validators.DataRequired()])
    last_name = StringField('Last name', [validators.DataRequired()])
    customer = StringField('Customer', [validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')
    #accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


class CleansingForm(FlaskForm):
    golive = StringField('Go live', validators=[validators.DataRequired()])
    entity = StringField('Entity', validators=[validators.DataRequired()])
    field = DateField('Field', validators=[validators.DataRequired()])
    description = StringField('Description', validators=[validators.DataRequired()])
    rule = StringField('Rule', validators=[validators.DataRequired()])
    active = BooleanField('Active')


class NumberSequenceForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired()])
    prefix = StringField('Prefix', validators=[validators.DataRequired()])
    start = IntegerField('Start', validators=[validators.DataRequired()])
    length = IntegerField('Length', validators=[validators.DataRequired()])


class ParameterForm(FlaskForm):
    parameter = StringField('Parameter', validators=[validators.DataRequired()])
    golive = SelectField('Go-live', validators=[validators.DataRequired()], filters=[lambda x: x or None])
    value = StringField('Value', validators=[validators.DataRequired()])