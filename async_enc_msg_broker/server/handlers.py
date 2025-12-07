import asyncio
import os
import sys 
from asyncio.streams import StreamWriter, StreamReader
from typing import Callable, Awaitable, Any
import json
import base64
import cloudpickle

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.queues import Queues
from utils.routes import RouteTbl
from utils.msg import deserialise_and_excute_objects

router= RouteTbl()

      
# Add message to a queue
@router.publish('add_msg')
async def publish_request(request:bytes, queue: Queues) -> None:
    
    #print(request)

    request_bytes_len= int.from_bytes(request[0:4], 'big')
    request_bytes= request[4: 4 + request_bytes_len]
    request_string= json.loads(request_bytes.decode('utf-8'))
    
    headers= request_string.get('headers')
    body= request_string.get('body')

    message= {
        'headers': headers,
        'body': body
    }
    message_bytes= json.dumps(message).encode('utf-8')
    message_bytes_len= len(message_bytes).to_bytes(4, 'big')
    queue_name= request_string.get('queue_name')
    
    await queue.push(
        message= message_bytes_len + message_bytes,
        queue_name= queue_name
    )

        #buffer= buffer[total_message:]


# Retrieve message from a queue
@router.consume('retv_msg')
async def consume_request(request:bytes, queue: Queues) -> bytes:
    request_bytes_len= int.from_bytes(request[0:4], 'big')
    request_bytes= request[4: 4 + request_bytes_len]
    request_string= json.loads(request_bytes.decode('utf-8'))
    queue_name= request_string.get('queue_name')

    
    message= await queue.pull(queue_name)

    if message is None:
        return "Please make sure the queue has messages. Try again!".encode('utf-8')
    return message

    


@router.add_scheduler('schedule_message')
async def schedule_message(request: bytes, queue: Queues):
    if not request:
        raise ValueError("No request is received")
    
    request_len= int.from_bytes(request[0:4], 'big')
    request_bytes= request[4: 4 + request_len]

    try:
        request_string= json.loads(request_bytes.decode('utf-8'))
    except json.JSONDecodeError:
        print(f"\n[SERVER]: Error deocding request")
    
    headers= request_string.get('headers')
    body= request_string.get('body')
    queue_name= request_string.get('queue_name')

    message={
        'headers': headers,
        'body': body
    }
    message_bytes= json.dumps(message).encode('utf-8')
    message_bytes_len= len(message_bytes).to_bytes(4, 'big')

    await queue.push(
        message=message_bytes_len + message_bytes,
        queue_name=queue_name
    )



@router.get_scheduler('get_scheduled_message')
async def get_scheduled_message(request: bytes, queue:Queues):
    if not request:
        raise ValueError('No request is sent')
    
    request_len= int.from_bytes(request[0:4], 'big')
    request_bytes= request[4: 4 + request_len]

    try:
        request_string= json.loads(request_bytes.decode('utf-8'))
    except json.JSONDecodeError:
        print(f"\n[SERVER]: Error decoding request")
    
    queue_name= request_string.get('queue_name')
    message= await queue.pull(queue_name=queue_name)
    if message is None:
        return None
    return message




    
            
            

            



            




