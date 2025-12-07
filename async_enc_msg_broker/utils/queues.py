import asyncio

class Queues:
    def __init__(self):
        self.queues= {}

    async def push(self, message:bytes, queue_name: str) -> None:
        if queue_name not in self.queues:
            self.queues[queue_name]= asyncio.Queue(maxsize=1000)
            print(f"New queue is added with name {queue_name}")
        queue= self.queues[queue_name]

        if not queue.full():
            await queue.put(message)
            print(f"New message is added to {queue_name}. New queue size: {queue.qsize()}")
        
        else:
            print(f"{queue_name} is full. Message is rejected")
    
    async def pull(self, queue_name:str) -> bytes:
        if queue_name not in self.queues:
            print(f"\nNo queue is created with name {queue_name}")
            return None
        
        queue= self.queues[queue_name]
        
        if not queue.empty():
            message= await queue.get()
            queue.task_done()
            print(f"\nMesssage is fetched successfully from {queue_name}. Remaining size: {queue.qsize()}")
            return message
        
        else:
            print(f"\n{queue_name} is empty. No message to fetch")
            return None





