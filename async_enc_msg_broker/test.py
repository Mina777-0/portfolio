from msgbroker.pro1.client.connect import ClientConnection
from msgbroker.pro1.utils.msg import Message
import uuid
from typing import Optional
from datetime import datetime, timezone, timedelta

class Demo:
    def __init__(self, host:str= "127.0.0.1"):
        self.host= host
        self.client: Optional[ClientConnection]= None

    async def connect(self):
        self.client= ClientConnection()
        try:
            await self.client.create_connection(host=self.host)

        except Exception as e:
            print(f"ERROR: {e}")

    async def publish_1(self):
        current_time= datetime.now(timezone.utc)
        expiry_time= current_time + timedelta(minutes=1)
        message= Message(
            body="This is test 1 - First message",
            content_type="application/json",
            correlation_id= uuid.uuid4().hex,
            kwargs={
                'exp': expiry_time.timestamp()
            }
        )
        try:
            if self.client:
                await self.client.publish_message(
                    message=message,
                    queue_name="queue_test1"
                    )
                
        except Exception as e:
            print(f"ERROR 1: {e}")
        
    async def publish_2(self):
        message= Message(
            body="This is test 2 - Second message",
            content_type="application/json",
            correlation_id= uuid.uuid4().hex
        )

        try:
            if self.client:
                await self.client.publish_message(
                    message=message,
                    queue_name='queue_test1'
                )
        except Exception as e:
            print(f"ERROR: {e}")

    async def publish_3(self):
        message= Message(
            body="This is test 3 - Different queue",
            content_type="application/json",
            correlation_id= uuid.uuid4().hex
        )

        try:
            await self.client.publish_message(
                message=message,
                queue_name='queue_test2'
            )
        except Exception as e:
            print(f"ERROR: {e}")

    async def add_job1(self):
        message= Message(
            body="This is the first scheduled message",
            correlation_id= uuid.uuid4().hex,
            scheduled_mode='interval'
        )

        try:
            await self.client.add_scheduler(
                message=message,
                minutes=0.5,
                queue_name='scheduled_queue_1'
            )
        except Exception as e:
            print(f"ERROR SCHEDULER: {e}")
    
    async def add_job2(self):
        message= Message(
            body="This is the second scheduled message",
            correlation_id= uuid.uuid4().hex,
            scheduled_mode='interval'
        )

        try:
            await self.client.add_scheduler(
                message=message,
                minutes=1,
                queue_name='scheduled_queue_1'
            )
        except Exception as e:
            print(f"ERROR SCHEDULER: {e}")

    async def add_job3(self):
        message= Message(
            body="This is the third scheduled message",
            correlation_id= uuid.uuid4().hex,
            scheduled_mode='interval'
        )

        try:
            await self.client.add_scheduler(
                message=message,
                minutes=1.1,
                queue_name='scheduled_queue_2'
            )
        except Exception as e:
            print(f"ERROR SCHEDULER: {e}")
    
    
    async def consume(self, queue_name):
        if self.client:
            try:
                
                response= asyncio.create_task(self.client.consume_message(queue_name))
                return await response
                    
            except Exception as e:
                print(f"Consume failed")

    async def get_job(self, queue_name):
        if self.client:
            try:
                response= asyncio.create_task(self.client.call_scheduler(queue_name))
                return await response
            except Exception as e:
                print(f"ERROR: Couldn't get scheduled message: {e}")

    
    

import asyncio

async def main():
    d= Demo()
    try:
        await d.connect()
        if d.client and d.client.writer:
            while True:
                service= await asyncio.to_thread(input, 'publish/consume c/p? ')
                if service.lower().strip() == 'p':
                
                    #task= await d.publish_1()
                    await asyncio.gather(d.publish_1(), d.publish_2(), d.publish_3())
                    await asyncio.gather(d.add_job1(), d.add_job2(), d.add_job3())
                    
        
                elif service.lower().strip() == 'c':
                    result= await d.consume('queue_test1')
                    print(result)
                    
                else:
                    continue

    except Exception as e:
        print(f"ERROR # {e}")
    
       

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("User closed the app")

