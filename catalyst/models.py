from app import db, login
# from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import backref, relationship
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime
from dataclasses import dataclass, field


@dataclass()
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    email: str
    password: str
    active: bool
    first_name: str
    last_name: str
    customer_id: str
    role: str

    id: int = db.Column(db.Integer, primary_key=True)

    # User Authentication fields
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    # User fields
    active = db.Column(db.Boolean(), default=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    customer_id = db.Column(db.String(20), db.ForeignKey('customers.id'), nullable=True)
    role = db.Column(db.String(20), nullable=True)

    # Relationships
    # roles = db.relationship('Role', secondary='user_roles')
    customer = relationship("Customer", back_populates="users")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_active(self):
        # override UserMixin property which always returns true
        # return the value of the active column instead
        return self.active

    @property
    def allowed_golives(self):
        # TODO: filter only on active golives
        golives = GoLive.query.filter(GoLive.customer_id == self.customer_id)
        allowed_golives = [gl.id for gl in golives]
        return allowed_golives


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

"""
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
"""


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(64))
    database_name = db.Column(db.String, nullable=False)
    # database_id = db.Column(db.Integer, db.ForeignKey('databases.id'), nullable=True)  # golive can be empty

    parameters = db.relationship("Parameter", back_populates="customer")
    translations = db.relationship("Translation", back_populates="customer")
    number_sequences = db.relationship("NumberSequence", back_populates="customer")
    databases = db.relationship("Database", back_populates="customer")
    # primary_database = db.relationship("Database", back_populates="customer")

    # relationships
    users = relationship("User", back_populates="customer")


class GoLive(db.Model):
    __tablename__ = 'golives'

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(64))
    customer_id = db.Column(db.String(20), db.ForeignKey('customers.id'), nullable=False)
    #database_name = db.Column(db.String())
    go_live_date = db.Column(db.Date)
    last_generated = db.Column(db.DateTime)
    # data_issues_dict = db.Column(db.String)
    parameters = db.relationship("Parameter", back_populates="golive")
    active = db.Column(db.Boolean, default=True)

    customer = db.relationship('Customer', backref=backref("customers", lazy="dynamic"), foreign_keys='GoLive.customer_id')
    entities = relationship("Entity", back_populates="golive", cascade="all,delete")
    translations = relationship("Translation", back_populates="golive")

    @property
    def toggle_activate(self):
        # override UserMixin property which always returns true
        # return the value of the active column instead
        if self.active is True:
            self.active = False
        else:
            self.active = True
        db.session.commit()

    def clone(self, new_golive):
        if GoLive.query.get(new_golive) is not None:
            print('Go live ' + new_golive + ' already exists')
            return None

        print('Cloning go-live ' + self.id + ' to ' + new_golive)
        d = dict(self.__dict__)
        # get old data before deleting it
        # d.pop("id")  # get rid of id
        # d['id'] =
        d.pop("_sa_instance_state")  # get rid of SQLAlchemy special attr

        # add _COPY suffix to new name
        d['id'] = new_golive
        copy = self.__class__(**d)

        try:
            db.session.add(copy)
            db.session.commit()  # if you need the id immediately
        except IntegrityError:
            return IntegrityError

        # copy all the entities to the new golive
        for entity in self.entities:
            entity.clone(new_golive=copy.id)

        return copy


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
    entity_group = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True, nullable=False)

    entity_fields = relationship("EntityField", back_populates="entity", cascade="all,delete")
    cleansing_rules = relationship("CleansingRule", back_populates="entity")
    export_details = relationship("ExportDetail", back_populates="entity")
    scope_rules = relationship("ScopeRule", back_populates="entity")

    __table_args__ = (
        # combination of entity & golive must be unique
        db.UniqueConstraint('entity', 'golive_id'),
    )

    # golive = db.relationship('GoLive', backref=backref("entity_golives", lazy="dynamic"), foreign_keys='Entity.golive_id')
    golive = relationship("GoLive", back_populates="entities")

    @property
    def toggle_activate(self):

        if self.active is True:
            self.active = False
        else:
            self.active = True
        db.session.commit()

    def clone(self, new_golive=None):
        print('Cloning entity ' + self.entity)
        d = dict(self.__dict__)
        # get old data before deleting it
        # d.pop("id")  # get rid of id
        d['id'] = None
        d.pop("_sa_instance_state")  # get rid of SQLAlchemy special attr

        if new_golive is None:
            d['entity'] = d['entity'] + ' _COPY'    # add _COPY suffix to new name only when copying for the same go-live
        else:
            d['golive_id'] = new_golive     # override golive if new_golive is filled

        copy = self.__class__(**d)

        try:
            db.session.add(copy)
            db.session.commit()     # if you need the id immediately
        except IntegrityError as e:
            # rollback & try additional _COPY suffix
            print(e)
            db.session.rollback()
            copy.entity = copy.entity + ' _COPY'
            db.session.add(copy)
            db.session.commit()

        # copy all the fields to the new enttiy
        for field in self.entity_fields:
            field.clone(new_id=copy.id, new_golive=new_golive)

        return copy


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
    parameter = db.Column(db.String(255))
    source_field = db.Column(db.String)
    translation_key = db.Column(db.String(255))
    regex_validation = db.Column(db.String)
    number_sequence_id = db.Column(db.String(20), db.ForeignKey('number_sequences.id'), nullable=False)
    transformation_rule = db.Column(db.String)

    # entity = db.relationship("Entity", backref=backref("entities", lazy="dynamic"))
    entity = db.relationship("Entity", back_populates="entity_fields")
    golive = db.relationship('GoLive', backref=backref("golives", lazy="dynamic"),
                               foreign_keys='EntityField.golive_id')
    number_sequence = db.relationship("NumberSequence", back_populates="entity_fields")
    scope_rules = db.relationship("ScopeRule", back_populates="entity_field")

    # combination of entity id & field name must be unique
    __table_args__ = (
        # combination of golive, translation_key & from_value must be unique
        db.UniqueConstraint('entity_id', 'field'),
    )

    def clone(self, new_id, new_golive=None):
        print('Cloning field ' + self.field)
        d = dict(self.__dict__)
        # d.pop("id")  # get rid of id
        d.pop("_sa_instance_state")  # get rid of SQLAlchemy special attr

        d['id'] = None
        d['entity_id'] = new_id

        if new_golive is not None:
            d['golive_id'] = new_golive  # to get the correct golive id

        copy = self.__class__(**d)
        db.session.add(copy)
        db.session.commit()  # if you need the id immediately


class Translation(db.Model):
    __tablename__ = 'translation_table'

    id = db.Column(db.Integer, primary_key=True)
    golive_id = db.Column(db.String(20), db.ForeignKey('golives.id'), nullable=False)
    customer_id = db.Column(db.String(20), db.ForeignKey('customers.id'), nullable=False)
    translation_key = db.Column(db.String(255), nullable=False)
    from_value = db.Column(db.String(500))
    to_value = db.Column(db.String)

    golive = db.relationship('GoLive', back_populates="translations")
    customer = db.relationship("Customer", back_populates="translations")

    __table_args__ = (
        # combination of golive, translation_key & from_value must be unique
        db.UniqueConstraint('customer_id','golive_id', 'translation_key', 'from_value'),
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
    active = db.Column(db.Boolean(), default=True)
    type = db.Column(db.String(20), nullable=False)

    # entity_id = db.Column(db.Integer, nullable=False)
    entity_field = db.relationship("EntityField", backref=backref("entity_fields", lazy="dynamic"),
                             foreign_keys='CleansingRule.entity_field_id')
    entity = db.relationship('Entity', back_populates="cleansing_rules")
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


class Parameter(db.Model):
    __tablename__ = 'parameters'

    id = db.Column(db.Integer, primary_key=True)
    parameter = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String, nullable=False)
    customer_id = db.Column(db.String(20), db.ForeignKey('customers.id'), nullable=False)
    golive_id = db.Column(db.String(20), db.ForeignKey('golives.id'), nullable=True)  # golive can be empty

    customer = db.relationship("Customer", back_populates="parameters")
    golive = db.relationship("GoLive", back_populates="parameters")

    __table_args__ = (
        # combination of parameter, golive & customer must be unique
        db.UniqueConstraint('parameter', 'golive_id', 'customer_id'),
    )


class ParameterQuery(object):
    @staticmethod
    def get_parameter(parameter, golive_id, customer_id=None):
        """
        The idea is to return parameter values dependent on the configuration:
            - if a parameter is set without go-live value, it's used as a general value for the customer in case, across
            all go-lives
            - it's possible to override this value for a specific go-live if you enter the go-live value
        """

        if customer_id is None:
            customer_id = current_user.customer_id

        param = Parameter.query.filter(and_(Parameter.parameter == parameter, Parameter.customer_id
                                            == customer_id, Parameter.golive_id == golive_id)).first()

        if param:
            return param.value
        else:
            param = Parameter.query.filter(and_(Parameter.parameter == parameter, Parameter.customer_id
                                                == customer_id, Parameter.golive_id == None)).first()
            return param.value if param else None


class NumberSequence(db.Model):
    __tablename__ = 'number_sequences'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    prefix = db.Column(db.String(255), nullable=False)
    start = db.Column(db.Integer, nullable=True)
    length = db.Column(db.Integer)
    customer_id = db.Column(db.String(20), db.ForeignKey('customers.id'), nullable=False)  # golive can be empty
    example = db.Column(db.String(255))

    entity_fields = db.relationship("EntityField", back_populates="number_sequence")
    customer = db.relationship("Customer", back_populates="number_sequences")

    def set_example(self):
        self.example = self.prefix + str(self.start).zfill(self.length)


class ExportDetail(db.Model):
    __tablename__ = 'export_details'

    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255))
    entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=False)

    entity = db.relationship('Entity', back_populates="export_details")


class Database(db.Model):
    __tablename__ = 'databases'

    id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(255))
    user = db.Column(db.String(255))
    password = db.Column(db.String)
    customer_id = db.Column(db.String(20), db.ForeignKey('customers.id'), nullable=False)
    usage = db.Column(db.String(255), default='primary')  # primary, legacy, loadfiles

    customer = db.relationship("Customer", back_populates="databases")

    __table_args__ = (
        # combination of parameter, golive & customer must be unique
        db.UniqueConstraint('customer_id', 'usage'),
    )

    """
    TO DO: encrypt & decrypt password
    https://www.geeksforgeeks.org/how-to-encrypt-and-decrypt-strings-in-python/
    """


class ScopeRule(db.Model):
    __tablename__ = 'scope_rules'

    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=False)
    entity_field_id = db.Column(db.Integer, db.ForeignKey('entity_fields.id'), nullable=False)

    entity = db.relationship('Entity', back_populates="scope_rules")
    entity_field = db.relationship('EntityField', back_populates="scope_rules")
