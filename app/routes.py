from flask import jsonify
from app import app
from catalyst.models import Entity

@app.route('/')
@app.route('/index')
def index_route():

    return("Hello world")


@app.route('/entities/')
def users():
  entity = Entity.query.all()
  return jsonify(entity)