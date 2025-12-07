from redis.asyncio import Redis
import redis.exceptions
import json 
import aio_pika
import asyncio
from log_config import get_log
import uuid
from email_config import email_verification, email_message


logger= get_log()
#logger.info("BROKER TEST")


# Caching with Redis

class RedisConfig:
    def __init__(self, url= 'redis://127.0.0.1:6379'):
        self.redis_url= url
        self.redis_client= None

    async def connect(self):
        try:
            self.redis_client= Redis.from_url(url=self.redis_url, decode_responses= True)
            await self.redis_client.ping()
        except redis.exceptions.ConnectionError as e:
            logger.debug(f"ERROR: Connection failed to redis server: {e}")
            self.redis_client=None
        except Exception as e:
            logger(f"An unexpected error occured: {e}")

        

    async def create_token(self, user_id:int) -> str:
        if self.redis_client is None:
            logger.error(f"No connection to redis server. Cannot set any values.")
            return None
        
        token= uuid.uuid4().hex

        await self.redis_client.set(name= token, value=user_id, ex=180)
        return token

    async def verify_token(self, token:str) -> int:
        if self.redis_client is None:
            logger.error(f"No connection to redis server. Cannot get any values")
            return None
        try:
            user_id= await self.redis_client.get(token)
            if user_id is None:
                return None
            return user_id
        
        except redis.exceptions.ConnectionError as e:
            logger.debug(f"ERROR: Connection to redis server failed {e}")
        except Exception as e:
            logger.debug(f"An unexpected error occured: {e}")

'''        
async def main():
    cach_client= RedisConfig()
    await cach_client.connect()

    #token= await cach_client.create_token(12)
    #print(token)
    
    user= await cach_client.verify_token('79497ef5cdf1408d95eaf8e8727cba98')
    print(user, type(user))
    user_= int(user)
    print(user_, type(user_))
    

asyncio.run(main())
'''

# AMQP CONFIGURATION

class AmqpPublishConfig:
    def __init__(self, amqp_url="amqp://guest:guest@127.0.0.1"):
        self.amqp_url= amqp_url
        self.connection= None
        self.channel= None
        self.exchange= None
        self.futures= {}

    async def connect(self):
        try:
            self.connection= await aio_pika.connect_robust(url=self.amqp_url, timeout=10.0)
            self.channel= await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)
            self.exchange= await self.channel.declare_exchange(name="logs", type= aio_pika.ExchangeType.DIRECT, durable= True, timeout=10.0)
        
        except aio_pika.exceptions.AMQPConnectionError as e:
            logger.error(f"ERROR: Connection to amqp failed ")
        except asyncio.TimeoutError:
            logger.error(f"No connection established or exchange declared. Time out")
        except Exception as e:
            logger.error(f"An unexpected error occured: {e}")

    async def publish_email(self, body:dict, **kwargs):
        try:
            if not self.channel or self.channel.is_closed:
                logger.debug(f"No open channel. Cannot publish email")
                return None
            
            correlation_id= uuid.uuid4().hex

            message= aio_pika.Message(
                body= json.dumps(body).encode('utf-8'),
                content_type= "application/json",
                correlation_id= correlation_id
            )

            try:

                await self.exchange.publish(
                    message=message,
                    routing_key= "email_logs",
                    timeout= 10.0
                )
                logger.info(f"Message with body {message.body} is published")
            except aio_pika.exceptions.ChannelClosed:
                logger.debug(f"Channel is closed. Cannot publish email")
            except asyncio.TimeoutError:
                logger.debug(f"No email publishing. Time out")


        except aio_pika.exceptions.AMQPConnectionError:
            logger.debug(f"Error in connection to amqp. Couldn't publish")
        except Exception as e:
            logger.debug(f"An unexpected error occured: {e}")



class AmqpConsumeConfig:
    def __init__(self, amqp_url= "amqp://guest:guest@127.0.0.1"):
        self.amqp_url= amqp_url
        self.connection= None
        self.channel= None
        self.exchange= None

    async def connect(self):
        try:
            self.connection= await aio_pika.connect_robust(url=self.amqp_url, timeout=10.0)
            self.channel= await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)
            self.exchange= await self.channel.declare_exchange(name='logs', type=aio_pika.ExchangeType.DIRECT, durable=True)

        except aio_pika.exceptions.AMQPConnectionError as e:
            logger.error(f"ERROR: Connection to amqp failed")
        except asyncio.TimeoutError:
            logger.error(f"No connection established or exchange declared. Time out")
        except Exception as e:
            logger.error(f"An unexpected error occured: {e}")

    async def email_consume(self):
        if not self.channel or self.channel.is_closed:
            logger.debug(f"No open channel. Cannot consume emails")
            return None
        
        try:
            queue= await self.channel.declare_queue(exclusive=True)

            try:
                await queue.bind(self.exchange, routing_key='email_logs', timeout=10.0)
            except asyncio.TimeoutError:
                logger.debug(f"No queue binding established. Time out")

            async for message in queue.iterator():
                async with message.process():
                    try:
                        body= json.loads(message.body.decode('utf-8'))
                    except json.JSONDecodeError:
                        logger.error(f"Error decoding message body")
                    try:    
                        await email_message(
                            to_email= body.get('to_email'),
                            subject= body.get('subject'),
                            param= body.get('otp')
                        )
                    except Exception as e:
                        logger.error(f"ERROR: couldn't send email notification: {e}")
        
        except aio_pika.exceptions.AMQPConnectionError:
            logger.error(f"Error in connection to amqp. Couldn't consume")
        except Exception as e:
            logger.error(f"An unexpected error occured: {e}")


                


        

        


