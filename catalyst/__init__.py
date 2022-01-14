from catalyst.loadfiles import create
from catalyst.reporting import generate_migration_dashboard
from catalyst.models import Task
from app import db
from datetime import datetime
from sqlalchemy.exc import ProgrammingError


def create_task(type, params):
    task = Task(type=type, parameters=params, created=datetime.now())

    db.session.add(task)
    db.session.commit()


def process_task(task):
    type = task.type
    params = task.parameters

    if type == 'create_loadfiles':
        try:
            task.status = 'processing'
            db.session.commit()

            create(params)
            task.status = 'completed'
            task.message = 'Loadfile generation succesful'
            task.completed = datetime.now()
        except ProgrammingError as e:
            task.status = 'error'
            task.message = str(e)
            task.completed = datetime.now()

    elif type == 'generate_dashboard':
        try:
            task.status = 'processing'
            db.session.commit()

            generate_migration_dashboard(params)
            task.status = 'completed'
            task.message = 'Migration dashboard updated'
            task.completed = datetime.now()
        except ProgrammingError as e:
            task.status = 'error'
            task.message = str(e)
            task.completed = datetime.now()

    else:
        task.status = 'error'
        task.message = 'Type not recognized'
        task.completed = datetime.now()

    db.session.commit()


def process_all_tasks():
    tasks = Task.query.filter_by(status='pending')
    num = tasks.count()
    print('Processing ' + str(num) + ' tasks')

    for task in tasks:
        process_task(task)

