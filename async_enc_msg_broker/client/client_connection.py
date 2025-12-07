import asyncio
import ssl 
import os 
import sys
import json
from asyncio.streams import StreamWriter, StreamReader
from typing import Optional, Any, Callable, Awaitable, Dict
from contextlib import asynccontextmanager
import cloudpickle
import base64
from datetime import datetime, timezone, timedelta
from time import sleep

utils_path= os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(utils_path)
#print(sys.path)
from utils.msg import Message, handle_response, Object
from utils.queues import Queues

cert_path= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cert.pem'))
'''
if os.path.exists(cert_path):
    print("yes")
else:
    print("NO")
'''

class ClientConnection:

    def __init__(self):
        self.reader: Optional[StreamReader]= None
        self.writer: Optional[StreamWriter]= None 
        self.minutes: Optional[int]= None
        self.date: Optional[datetime]= None
        self.scheduler: Dict[str, Callable[..., Awaitable[Any]]]={}

        
    async def create_connection(self, host: str, port= 2547):
        context= ssl.create_default_context()
        context.check_hostname= False
        context.verify_mode= ssl.CERT_REQUIRED

        try:
            context.load_verify_locations(cert_path)
        except FileNotFoundError:
            print(f"[CLEINT]: 'cert.pem' is missing")
            return
        
        try:
            reader, writer= await asyncio.open_connection(
                host=host,
                port= port,
                ssl=context,
                server_hostname= host,
                ssl_handshake_timeout= 10.0
            )

            
            server_addr= writer.get_extra_info('peername')
            ssl_obj= writer.get_extra_info('ssl_object')
            print(f"\n[CLIENT]: Secure connection is opened with server {server_addr}")
            print(f"\n[CLIENT]: SSL/TLS handshake is successful. Protocol: {ssl_obj.version()} | Cipher: {ssl_obj.cipher()}")

            self.reader= reader
            self.writer= writer

        except ConnectionResetError:
            print(f"[CLIENT]: Connection is failed. Is the server running?")
        except ssl.SSLCertVerificationError:
            print(f"[CLIENT]: Certificate verification failed.")
        except Exception as e:
            print(f"[CLIENT]: An unexpected error occured: {e}")
        



    async def publish_message(self, message: Message, queue_name: str):
        
        if self.writer is None or self.writer.is_closing():
            print(f"No connection or Writer is closing. Cannot publish message")
            return None
        
        req_metadata={
            'path': 'add_msg',
            'method': 'publish'
        }

        #msg_body= message.body
        headers= {
            'content-type': message.content_type,
            'correlation_id': message.correlation_id,
            'content-length': len(message.body)
        }
        body= {
            'body': message.body,
            'kwargs': message.kwargs
        }
    
        complete_message={
            'req_metadata': req_metadata,
            'headers': headers,
            'body': body,
            'queue_name': queue_name 
        }
        complete_message_bytes= json.dumps(complete_message).encode('utf-8')
        complete_message_bytes_len= len(complete_message_bytes).to_bytes(4, 'big')


        self.writer.write(complete_message_bytes_len + complete_message_bytes)
        await self.writer.drain()
        #print("message is sent successfully")
        

        


    async def consume_message(self, queue_name: str):
        
        if self.writer is None or self.writer.is_closing():
            print(f"No connection or writer is closed. Cannot consume message")
            return
        
        req_metadata={
            'path': "retv_msg",
            'method': 'consume',
        }

        headers={
            'content-type': "application-json",
            'correlation_id': "",
            'content_length': 0
        }

        complete_message= {
            'req_metadata': req_metadata,
            'headers': headers,
            'body': "",
            'queue_name': queue_name
        }

        complete_message_bytes= json.dumps(complete_message).encode('utf-8')
        complete_message_bytes_len= len(complete_message_bytes).to_bytes(4, 'big')
    
    
        self.writer.write(complete_message_bytes_len + complete_message_bytes)
        await self.writer.drain()
        
        try:
            return await self.recv_response()
        except Exception as e:
            print(f"[CLIENT]: No messages received: {e}")

    
    # Add a scheduler job
    async def add_scheduler(
            self, 
            message:Message, 
            queue_name:str, 
            minutes: float | None= None, 
            date: datetime | None= None
    ):
        if self.writer is None or self.writer.is_closing():
            print(f"No connection or writer is closed. Cannot schedule a message")
            return None
        
        req_metadata= {
            'path': "schedule_message",
            'method': "add_scheduler"
        }

        headers={
            'content-type': message.content_type,
            'content-length': len(message.body),
            'correlation_id': message.correlation_id
        }

        body={
            'body': message.body,
            'kwargs': message.kwargs
        }

        request= {
            'req_metadata': req_metadata,
            'headers': headers,
            'body': body,
            'queue_name': queue_name
        }

        if message.scheduled_mode == 'interval':
            message_id= message.correlation_id
            delayed_seconds= minutes * 60
            #print(f"Delayed seconds: {delayed_seconds}")
            try:
                task= asyncio.create_task(self._timer(
                    message_id=message_id,
                    queue_name=queue_name,
                    delayed_seconds=delayed_seconds
                ))
                #print(f"\n[CLIENT]: timer task is scheduled")
            except Exception as e:
                print(f"\n[CLEINT]: Couldn't schedule the timer task")

            #self.scheduler[message.correlation_id]={}
            self.scheduler[message.correlation_id]= task
            

        elif message.scheduled_mode == 'date':
            #self.scheduler[message.correlation_id]={}
            self.scheduler[message.correlation_id]= queue_name

        print(f"Scheduler: {self.scheduler}")
        
        
        request_bytes= json.dumps(request).encode('utf-8')
        request_bytes_len= len(request_bytes).to_bytes(4, 'big')

        self.writer.write(request_bytes_len + request_bytes)
        await self.writer.drain()
        #print(f"\n[CLIENT]: Message is scheduled successfully")

       
        
    async def _timer(self, message_id:str, queue_name:str, delayed_seconds:float):
        try:

            print("SCHEDULER IS RUNNING")
            if message_id in self.scheduler:
                print(f"message_id: {message_id}")
                print(f"delayed seconds: {delayed_seconds}")
                
                # Keep the loop free until time
                await asyncio.sleep(delayed_seconds)

                # Schedule this task to await for what the recv_message return
                task= asyncio.create_task(self.call_scheduler(queue_name))
                await asyncio.to_thread(print, f"\n[SCHEDULER]: Message {message_id} is fired to queue {queue_name}")

                self.scheduler.pop(message_id)
                
                return await task

                

            else:
                print(f"\n[SCEHDULER]: No message is schdeduled")

        except asyncio.CancelledError:
            print(f"\n[SCEHDULER]: Message {message_id} was cancelled")
        except Exception as e:
            print(f"\n[SCHEDULER]: An unexpected error while firing message {message_id}: {e}") 


        
    # Run a scheduler job 
    async def call_scheduler(self, queue_name:str):
        if self.writer is None or self.writer.is_closing():
            print("No connection or writer is closed. Cannot call a scheduled messsage")
            return None
        
        req_metadata= {
            'path': "get_scheduled_message",
            'method': "get_scheduler"
        }

        headers={
            'content-type': 'application/json',
            'content-length': 0,
            'correlation_id': ''
        }

        body={
            'body': '',
            'kwargs': ''
        }

        request= {
            'req_metadata': req_metadata,
            'headers': headers,
            'body': body,
            'queue_name': queue_name
        }

        request_bytes= json.dumps(request).encode('utf-8')
        request_bytes_len= len(request_bytes).to_bytes(4, 'big')

        #await asyncio.to_thread(print, f"Message is about to be sent { queue_name}")
        self.writer.write(request_bytes_len + request_bytes)
        await self.writer.drain()
        #print(f"[CLIENT]: scheduled message is sent successfully")

        try:
            print(await self.recv_response())
        except Exception as e:
            print(f"\n[CLIENT] No message is received: {e}")

        

    async def recv_response(self):
        buffer= b''
        while True:
            data= await self.reader.read(4096)
            if not data:
                break
            buffer += data
            #print(f"[CLIENT]: Initial buffer received from Server{buffer}")
            if len(buffer) < 4:
                break

            total_message_len= int.from_bytes(buffer[0: 4], 'big')
            if len(buffer) < total_message_len:
                break

            complete_message= buffer[0: 4 + total_message_len]
            message= handle_response(complete_message)
            if message is None:
                break

            buffer= buffer[4 + total_message_len:]
            #print(f"[CLIENT]: Final buffer: {buffer}")

            return message
        
            #print(message)


