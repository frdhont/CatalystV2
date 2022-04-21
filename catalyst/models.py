from app import db, login
# from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import backref
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User Authentication fields
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    # User fields
    active = db.Column(db.Boolean(), default=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    customer = db.Column(db.String(20), db.ForeignKey('customers.id'), nullable=True)

    # Relationships
    roles = db.relationship('Role', secondary='user_roles')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_active(self):
        # override UserMixin property which always returns true
        # return the value of the active column instead
        return self.active


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(64))
    database_name = db.Column(db.String, nullable=False)


class GoLive(db.Model):
    __tablename__ = 'golives'

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(64))
    customer_id = db.Column(db.String(20), db.ForeignKey('customers.id'), nullable=False)
    #database_name = db.Column(db.String())
    go_live_date = db.Column(db.Date)
    last_generated = db.Column(db.DateTime)
    # data_issues_dict = db.Column(db.String)

    customer = db.relationship('Customer', backref=backref("customers", lazy="dynamic"), foreign_keys='GoLive.customer_id')


class Entity(db.Model):
    __tablename__ = 'entities'

    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String(255), nullable=False)
    golive_id = db.Column(db.String(20), db.ForeignKey('golives.id'), nullable=False)
    description = db.Column(db.String(255))
    source_view = db.Column(db.String(500))
    target_system = db.Column(db.String(500))
    validation_json = db.Column(db.String)
    scope_column = db.Column(db.String(255), default='in_scope')
    allow_unknown = db.Column(db.Boolean, default=True)
    code_column = db.Column(db.String(255), nullable=False, default='code')
    data_cleansing_json = db.Column(db.String)

    __table_args__ = (
        # combination of entity & golive must be unique
        db.UniqueConstraint('entity', 'golive_id'),
    )

    golive = db.relationship('GoLive', backref=backref("entity_golives", lazy="dynamic"),
                             foreign_keys='Entity.golive_id')


class EntityField(db.Model):
    __tablename__ = 'entity_fields'

    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=False)
    golive_id = db.Column(db.String(20), db.ForeignKey('golives.id'), nullable=False)
    field = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    precision = db.Column(db.Integer)
    allow_null = db.Column(db.Boolean(64), nullable=False)
    description = db.Column(db.String(255))
    mapping_type = db.Column(db.String(50))
    default_value = db.Column(db.String)
    source_field = db.Column(db.String)
    translation_key = db.Column(db.String(255))
    regex_validation = db.Column(db.String)

    entity = db.relationship("Entity", backref=backref("entities", lazy="dynamic"))
    golive = db.relationship('GoLive', backref=backref("golives", lazy="dynamic"),
                               foreign_keys='EntityField.golive_id')


class Translation(db.Model):
    __tablename__ = 'translation_table'

    id = db.Column(db.Integer, primary_key=True)
    golive = db.Column(db.String(20), db.ForeignKey('golives.id'), nullable=False)
    translation_key = db.Column(db.String(255), nullable=False)
    from_value = db.Column(db.String(500))
    to_value = db.Column(db.String)

    __table_args__ = (
        # combination of golive, translation_key & from_value must be unique
        db.UniqueConstraint('golive', 'translation_key', 'from_value'),
    )


class CleansingRule(db.Model):
    __tablename__ = 'cleansing_rules'

    id = db.Column(db.Integer, primary_key=True)
    # golive = db.Column(db.String(20), db.ForeignKey('golives.id'), nullable=False)

    entity_field_id = db.Column(db.Integer, db.ForeignKey('entity_fields.id'), nullable=False)
    entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=False)
    golive_id = db.Column(db.String(20), db.ForeignKey('golives.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    rule = db.Column(db.String)
    criteria = db.Column(db.String)
    active = db.Column(db.Boolean())

    # entity_id = db.Column(db.Integer, nullable=False)
    entity_field = db.relationship("EntityField", backref=backref("entity_fields", lazy="dynamic"),
                             foreign_keys='CleansingRule.entity_field_id')
    entity = db.relationship('Entity', backref=backref("cleansingrule_entities", lazy="dynamic"),
                             foreign_keys='CleansingRule.entity_id')
    golive = db.relationship('GoLive', backref=backref("cleansingrule_golives", lazy="dynamic"),
                             foreign_keys='CleansingRule.golive_id')


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255), nullable=False)
    parameters = db.Column(db.String, nullable=False)
    status = db.Column(db.String(255), default='pending')
    message = db.Column(db.String)
    created = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.DateTime)
