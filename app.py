from app import app
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from catalyst import process_all_tasks
import os

# Creates a default Background Scheduler
sched = BackgroundScheduler()
sched.add_job(process_all_tasks, 'interval'
              , minutes=int(os.getenv('TASK_PROCESSOR_INTERVAL')))  # interval time as env variable

# Starts the Scheduled jobs
sched.start()
print('Scheduler started')
atexit.register(lambda: sched.shutdown(wait=True))  # stop job when app stops, but wait untill all jobs are finished

# start web app
if __name__ == "__main__":
    app.run()

