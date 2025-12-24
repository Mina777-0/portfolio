import asyncio
import json 
from asyncio import StreamReader, StreamWriter
import os, sys, ssl
from dotenv import load_dotenv
from typing import Optional

env_file= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
'''
if os.path.exists(env_file):
    print("YES")
else:
    print("NO")
'''

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))

#print(sys.path)
from utils.queues import QueueManager
from job_handler import worker


load_dotenv(env_file)
password= os.environ.get('PASSWORD')
password_bytes= bytes(password, encoding='utf-8')




class ConnectionHandler:
    def __init__(self):
        self.queues: Optional[QueueManager]= None  
             

    def add_queues(self, queues):
        self.queues= queues


    async def __call__(self, reader: StreamReader, writer: StreamWriter):
        buffer= b''

        try:
            while True:
                data= await reader.read(2048)

                if not data:
                    break
                buffer += data
                #print(buffer)
                
                while True:
                    if len(buffer) < 4:
                        break
                    
                    req_bytes_len= int.from_bytes(buffer[0:4], 'big')
                    req_bytes= buffer[4: 4 + req_bytes_len]


                    try:
                        json_dict= json.loads(req_bytes.decode('utf-8'))
                    except json.JSONDecodeError:
                        print(f"\n[SERVER]: Error in decoding the request data")


                    released_job= {
                        'request_data': json_dict,
                        'addr': writer.get_extra_info('peername'),
                        'writer': writer
                    }
                    

                    # add job to the queue
                    await self.queues.add_task(task= released_job)

                    
                    buffer= buffer[4 + req_bytes_len: ]
                    print(buffer)

        except ConnectionResetError as e:
            print(f"\n[SERVER]: User reset connection: {e}")
        except BrokenPipeError as e:
            print(f"\n[SERVER]: Pipe is broken: {e}")
        except Exception as e:
            print(f"\n[SERVER]: An unexpected error occured: {e}")

    

        