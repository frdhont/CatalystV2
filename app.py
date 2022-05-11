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
atexit.register(lambda: sched.shutdown(wait=False))  # stop job if app is not running

# start web app
if __name__ == "__main__":
    app.run()

