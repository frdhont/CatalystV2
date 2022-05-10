from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SelectField, TextAreaField, BooleanField
from wtforms.fields import EmailField, DateField
from wtforms.widgets import TextArea


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
    description = StringField('Description')
    allow_null = BooleanField('Allow empty')
    mapping_type = SelectField('Mapping type', validators=[validators.DataRequired()], choices=[('default', 'Default')
        , ('one_to_one', 'One to one'), ('translation', 'Translation'), ('parameter', 'Parameter')])
    default = StringField('Default value', filters=[lambda x: x or None])  # lambda to insert NULL instead of "" to sql
    parameter = StringField('Parameter', filters=[lambda x: x or None])
    source_field = StringField('Source field', filters=[lambda x: x or None])
    translation_key = SelectField('Translation key',validators=[validators.Optional()], filters=[lambda x: x or None])
    regex_validation = StringField('Regex validation', filters=[lambda x: x or None])


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
