from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import sys 
from contextlib import asynccontextmanager

load_dotenv('.env')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.log_config import get_log

logger= get_log()
#logger.info('DATABASE TEST')

username= os.environ.get('DATABASE_USER')


DATABASE_URL= f'postgresql+asyncpg://{username}@127.0.0.1:5432/test3db'

engine= create_async_engine(DATABASE_URL)
#logger.info(f'Pool status: {engine.pool.status()}')

AsyncSessionLocal= async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


async def get_db_session():
    global logger, AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.debug(f"ERROR: couldn't create db session: {e}")
            raise 


@asynccontextmanager
async def scheduler_db_session():
    global logger, AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()

        except Exception as e:
            await session.rollback()
            logger.debug(f"ERROR: couldn't create scheduler db session: {e}")
            raise 
