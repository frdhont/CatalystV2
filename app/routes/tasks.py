from app import app, db
from flask import jsonify, request
from flask_login import login_required
from catalyst.models import Task
from datetime import datetime

@app.route('/tasks/create_loadfiles')
@login_required
# @roles_required('admin')
def tasks_create():
    type = request.args.get('type')
    params = request.args.get('params')

    if type is None or params is None:
        return jsonify({'error': 'type & params are mandatory'}), 400
    else:
        tasks = Task(type=type, parameters=params, created=datetime.now())
        db.session.add(tasks)
        db.session.commit()


    return jsonify('OK')