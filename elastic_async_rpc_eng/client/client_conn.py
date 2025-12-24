import asyncio, json 
from asyncio import StreamReader, StreamWriter
import os, sys, ssl 
from typing import Optional, Annotated, Dict
from urllib.parse import urlparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.schemas import PublishJobError, RpcMessage, Unit


cert_file= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cert.pem'))


class ClientConnection:
    timeout: Annotated[float, Unit(name='seconds')]
    futures: Dict[str, asyncio.Future]

    def __init__(self, **kw):
        self.reader: Optional[StreamReader]= None
        self.writer: Optional[StreamWriter]= None
        self.url: str= None
        self.timeout= kw.get('job_timeout') if kw else 60.0
        self.futures= {}


    async def url_connection(self, url:str):
        global cert_file

        try:
            parsed_uri= urlparse(url, scheme='arpc')

            username= parsed_uri.username
            password= parsed_uri.password
            hostname= parsed_uri.hostname
            port= parsed_uri.port if parsed_uri else 2547

            # Check for the username and password validty

        except Exception as e:
            print(f"\n[CLIENT]: URL configuration failed")

        context= ssl.create_default_context()
        context.check_hostname= False
        context.verify_mode= ssl.CERT_REQUIRED

        try:
            context.load_verify_locations(cert_file)
        except FileNotFoundError:
            print(f"\n[CLIENT]: 'cert.pem' file is not found")
        
        try:
            reader, writer= await asyncio.open_connection(
                host=hostname,
                port=port,
                ssl= context,
                server_hostname= hostname,
                ssl_handshake_timeout= 10.0
            )

            server_addr= writer.get_extra_info('peername')
            ssl_obj= writer.get_extra_info('ssl_object')

            print(f"\n[CLIENT]: Connection is established with server {server_addr}")
            print(f"\n[CLIENT]: SSL/TLS handshake is successful. Protocol: {ssl_obj.version()} | Cipher: {ssl_obj.cipher()}")

            self.reader= reader
            self.writer= writer


        except ConnectionError as e:
            print(f"\n[CLIENT]: Connectino failed. Is the server running. {e}")
        except BrokenPipeError as e:
            print(f"\n[CLIENT]: Pipe is broken: {e}")
        except Exception as e:
            print(f"\n[CLIENT]: An unexpected error occured: {e}")
        
    
    # Send a job to the server
    async def publish_job(self, message: RpcMessage):
        if self.writer is None or self.writer.is_closing():
            raise PublishJobError(f'[CLIENT]: Writer is None or closing')
        
        future= asyncio.get_running_loop().create_future()
        if message.id not in self.futures:
            self.futures[message.id]= future
        #print(f"Publishing messages with method {message.method}")
        
        json_message_bytes= json.dumps(message.request_data()).encode('utf-8')
        json_message_bytes_len= len(json_message_bytes).to_bytes(4, 'big')
        #print(f"Published msg: {json_message_bytes_len + json_message_bytes}")

        try:
            self.writer.write(json_message_bytes_len + json_message_bytes)
            await self.writer.drain()

        except Exception as e:
            raise PublishJobError(f"ERROR: {e}")
        
        response= await future
        del self.futures[message.id]
        print(response)

        


    async def recv_results(self):
        print(f"Recv-results is called")
        buffer= b''
        while True:
            data= await self.reader.read(2048)
            if not data:
                break
            buffer += data

            if len(buffer) < 4:
                break

            result_bytes_len= int.from_bytes(buffer[0:4], 'big')
            result_bytes= buffer[4: 4 + result_bytes_len]

            result_json= json.loads(result_bytes.decode('utf-8'))
            req_id= result_json.get('id')

            if req_id in self.futures:
                self.futures[req_id].set_result(result_json.get('result'))


            buffer= buffer[4 + result_bytes_len: ]

        


        