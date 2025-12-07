from app import create_app
import uvicorn
import uvloop
import asyncio
import multiprocessing
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'schedules')))
from schedules.db_tasks import unverified_users_reminder_task


def run_web_process():

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    uvicorn.run(
        app='main:create_app',
        factory=True,
        host='127.0.0.1',
        port= 8080, 
        reload=True,
        loop= 'uvloop'
    )

def run_scheduler_process():
    unverified_users_reminder_task()

def start_multiprocesses():
    web_process= multiprocessing.Process(target=run_web_process)
    schedule_process= multiprocessing.Process(target=run_scheduler_process)

    web_process.start()
    schedule_process.start()

    web_process.join()
    schedule_process.join()

if __name__ == "__main__":
    multiprocessing.set_start_method(method="spawn", force=True)
    start_multiprocesses()
    