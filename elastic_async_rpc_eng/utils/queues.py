from typing import Dict, Callable, Awaitable, Any, Annotated
import asyncio
from schemas import Unit, QueueEmptyError, QueueFullError, QueueNameError, QueueCreationError
import random 
import string




QueueDict= Dict[str, asyncio.Queue]

class QueueManager:
    queues: QueueDict
    timeout: Annotated[float, Unit(name='seconds')]

    def __init__(self, **kw):
        self.queues= {}
        self.queues_names= set()
        self.timeout= kw.get('queue_timeout') if kw else 10.0
        self.queue_name:str= ""

    
    def initialise_queue(self) -> None:
        queue_name= 'queue-'+ ''.join(random.choice(string.ascii_lowercase)) + ''.join(random.choices(string.digits, k=2))
        self.queue_name= queue_name

        if self.queue_name in self.queues_names:
            self.initialise_queue()
        
        if len(self.queues_names) == 5:
            raise QueueCreationError('[QUEUE MANAGER]: Cannot initialise new queues')
        
        self.queues_names.add(queue_name)

        self.queues[queue_name]= asyncio.Queue(maxsize=1000)
        print(f"\n[QUEUE MANAGER]: New queue {self.queue_name} is added to the pool")




    async def add_task(self, task: dict) -> None:

        queue= self.queues[self.queue_name]

        try:
            await asyncio.wait_for(queue.put(task), timeout=self.timeout)
            print(f"\n[QUEUE MANAGER]: Task {task['request_data']['id']} is added to {self.queue_name}. Queue-size: {queue.qsize()}")

        except asyncio.TimeoutError:
            print(f"[QUEUE MANAGER]: Queue '{self.queue_name}' is busy")
            
            try:
                # Initialise a new queue and call add task again to add the current task. If add task is not called, the current task is lost. The next task will be added 
                # to the new queue

                self.initialise_queue()
                await self.add_task(task)

            except QueueCreationError as e:
                print(f"\n[QUEUE MANAGER]: ERROR: {e}")
                raise QueueFullError('Queue is busy')



    async def pull_task(self, queue_name: str) -> dict:
        if queue_name not in self.queues_names:
            raise QueueNameError('Queue name is invalid')
        
        queue= self.queues[queue_name]

        try:
            task= await asyncio.wait_for(queue.get(), timeout= self.timeout)
            print(f"\n[QUEUE MANAGER]: Task {task['request_data']['id']} is fetched successfully from {queue_name}. Queue-size: {queue.qsize()}")

            return task 

        except asyncio.TimeoutError:
            print(f"\n[QUEUE MANAGER]: No task is found")
            raise QueueEmptyError('Queue is empty')


    

