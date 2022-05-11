from catalyst.loadfiles import create
from catalyst.reporting import generate_migration_dashboard, data_cleaning
from catalyst.models import Task, GoLive, Entity
from app import db
from pyodbc import IntegrityError
from datetime import datetime
from sqlalchemy.exc import ProgrammingError, DataError


def create_task(type, params):
    task = Task(type=type, parameters=params, created=datetime.now())

    db.session.add(task)
    db.session.commit()


def process_task(task):
    type = task.type
    params = task.parameters
    id = task.id

    try:
        task.status = 'processing'
        db.session.commit()

        task = task.query.get(id)

        if type == 'create_loadfiles':
            create(params)
            task.message = 'Loadfile generation succesful'

        elif type == 'generate_dashboard':
            generate_migration_dashboard(params)
            task.message = 'Migration dashboard updated'

        elif type == 'generate_data_issues':
            data_cleaning.generate_data_issues(params)
            task.message = 'Data issues generated'

        elif type == 'clone_golive':
            params = params.split(',')
            clone_golive = params[0]
            new_golive = params[1]

            golive = GoLive.query.get(clone_golive)
            if golive.clone(new_golive=new_golive) is None:
                task.message = 'Golive C01 already exists'
            else:
                task.message = 'Golive cloned'

        else:
            task.status = 'error'
            task.message = 'Type not recognized'
            task.completed = datetime.now()

        task.status = 'completed'
        task.completed = datetime.now()

        db.session.commit()

    except (KeyError) as e:
        print(e)
        db.session.rollback()
        task = Task.query.get(id)
        task.status = 'error'
        task.message = str(e)
        task.completed = datetime.now()
        db.session.commit()


def process_all_tasks():
    tasks = Task.query.filter_by(status='pending')
    num = tasks.count()
    print('Processing ' + str(num) + ' tasks')

    for task in tasks:
        process_task(task)

