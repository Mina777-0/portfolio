from fastapi import FastAPI
import os, sys
from contextlib import asynccontextmanager
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'database')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'views')))


from utils.cache_broker import AmqpConsumeConfig
from database.models import create_tables
from views.handlers import router
from utils.log_config import get_log


    

logger= get_log()
#logger.info("APP TEST")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global logger
    await create_tables()
    logger.info("Tables are created")

    amqp_client= AmqpConsumeConfig()
    try:
        await amqp_client.connect()
        logger.info('AMQP connection is established')
        asyncio.create_task(amqp_client.email_consume())
        logger.info('AMQP Consuming client is waiting ...')
    except Exception as e:
        logger.info(f"ERROR in AMQP connection: {e}")

    yield 


def create_app():
    app= FastAPI(lifespan=lifespan)

    origins= [
        '*.ngrok-free.app',
        'http://127.0.0.1:8080',
        'http://127.0.0.1:8000'
        'http://127.0.0.1'
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins= origins,
        allow_headers=['*'],
        allow_methods= ['*'],
        allow_credentials= True, 
        max_age= 600 
    )

    
    trusted_hosts= [
        'api.yourdomain.com', 
        'localhost',
        '127.0.0.1',
        '*.ngrok-free.app'
    ]

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts,
    )

    #app.add_middleware(HTTPSRedirectMiddleware) 

    
    app.add_middleware(
        GZipMiddleware,
        minimum_size= 1000, 
        compresslevel= 5 
    )

    app.include_router(router)

    return app 

