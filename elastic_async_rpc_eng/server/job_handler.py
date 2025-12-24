import asyncio
import json 
import sys, os 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.queues import QueueManager
from utils.schemas import QueueEmptyError
from utils.services import ServiceRouter

from typing import Dict, Callable, Awaitable, Any, Set, Optional


class WorkersManager:
    def __init__(self, queue_manager: QueueManager, **kw):
        self.queue_manager= queue_manager
        self.task: asyncio.Task= None
        self.number_worker: int= kw.get('number_worker') if kw else 1
        self.worker_tasks= []
        self.service_router: Optional[ServiceRouter]= None



    def add_service_router(self, router:ServiceRouter):
        self.service_router= router


    async def start_processes(self):
        for q_name in list(self.queue_manager.queues_names):
            # I can add more workers per queue
            for i in range(self.number_worker):
                self.task= asyncio.create_task(self.worker(queue_name=q_name))
                self.worker_tasks.append(self.task)
                print(f"\n[WORKER MANAGER]: Started {len(self.worker_tasks)} persistnet workers")

        
                
    async def worker(self, queue_name: str):
        service_router= self.service_router.Router

        while True:
            try:
                job= await self.queue_manager.pull_task(queue_name)
                #print(f"Job {job} is with worker {self.task}")
            except Exception as e:
                print(f"\n[WORKER MANAGER]: {e}. Waiting for jobs ..")
                continue
                

            method= job['request_data']['method']
            params= job['request_data']['params']
            id= job['request_data']['id']
            addr= job['addr']
            writer= job['writer']

            result= None

            if method in service_router:
                if method == 'server.stat':
                    handler= service_router[method]
                    result= handler(len(self.queue_manager.queues_names))

                else:
                    handler= service_router[method]
                    result= handler(*params)
            
            else:
                result ={
                    'code': -32601,
                    'message': 'Method not found'
                }
            

            #result= params[0] + params[1]

            message_dict= {
                'jsonrpc': "2.0",
                'id': id,
                'method': method,
                'result': result,
                'addr': addr
            }

            
            message_bytes=json.dumps(message_dict).encode('utf-8')
            message_bytes_len= len(message_bytes).to_bytes(4, 'big')

            writer.write(message_bytes_len + message_bytes)
            await writer.drain()


    async def close_worker(self):
        # Check if the queue is empty
        for q_name in list(self.queue_manager.queues_names):
            queue= self.queue_manager.queues[q_name]

            if not queue.empty():
                print(f"\n[WORKER MAANGER]: Draining {queue.qsize()} tasks from {q_name}")
                await asyncio.sleep(10.0)


        if self.worker_tasks:
            print(f"\n[WORKER MANAGER]: Worker manager is shutting {len(self.worker_tasks)} worker down ..")
            for task in self.worker_tasks:
                task.cancel()
                
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        self.worker_tasks.clear()





                
            
            












