from app import db
from sqlalchemy import ForeignKeyConstraint


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(64))


class GoLive(db.Model):
    __tablename__ = 'golives'

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(64))
    customer = db.Column(db.String(20), db.ForeignKey('customers.id'), nullable=False)
    database_name = db.Column(db.String)


class Entity(db.Model):
    __tablename__ = 'entities'

    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String(255), nullable=False)
    golive = db.Column(db.String(20), db.ForeignKey('golives.id'), nullable=False)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    source_view = db.Column(db.String(500))
    target_system = db.Column(db.String(500))
    validation_json = db.Column(db.String)
    scope_column = db.Column(db.String(255))

    __table_args__ = (
        # combination of entity & golive must be unique
        db.UniqueConstraint('entity', 'golive'),
    )


class EntityField(db.Model):
    __tablename__ = 'entity_fields'

    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.Integer, nullable=False)
    field = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    precision = db.Column(db.Integer)
    allow_null = db.Column(db.Boolean(64), nullable=False)
    description = db.Column(db.String(255))
    mapping_type = db.Column(db.String(50))
    default_value = db.Column(db.String)
    source_field = db.Column(db.String)
    translation_key = db.Column(db.String(255))


    __table_args__ = (
        # combination of entity & field must be unique
        db.UniqueConstraint('entity', 'field'),
    )


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