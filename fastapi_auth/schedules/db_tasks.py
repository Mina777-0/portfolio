import os, sys 
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from datetime import datetime, timezone, timedelta
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))

from utils.email_config import email_message
from database.models import User
from database.dbs import scheduler_db_session
from utils.log_config import get_log

logger= get_log()


async def unverified_users_reminder():
    current_time= datetime.now(timezone.utc)
    delayed_time= current_time - timedelta(days=1)

    try:
        async with scheduler_db_session() as db_session:
            stmt= select(User).where(
                User.created_at < delayed_time,
                User.email_verified == False
            )
            q_results= await db_session.execute(stmt)
            unverified_users= q_results.scalars().all()


            for user in unverified_users:
                body= f"Please, verify your email address or your registration will be terminated in 24 hours"
                try:
                    await email_message(
                        to_email=user.email,
                        subject="Email Verification Reminder",
                        body=body
                    )
                except Exception as e:
                    logger.error(f"Couldn't send unverified reminder email {e}")

    except Exception as e:
        logger.debug("An unexpected error with scheduled remindering task")



def unverified_users_reminder_task():
    
    loop= asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    scheduled_task= AsyncIOScheduler(event_loop=loop)

    if not scheduled_task.running:
        scheduled_task.add_job(
            unverified_users_reminder,
            'interval',
            minutes= 30
        )
        try:
            scheduled_task.start()
            
            loop.run_forever() 
        except (KeyboardInterrupt, SystemExit):
            if scheduled_task.running:
                scheduled_task.shutdown(wait=False)





