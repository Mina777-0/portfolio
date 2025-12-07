from asyncio.streams import StreamReader, StreamWriter
import asyncio
import os, sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Optional

from utils.queues import Queues
from utils.routes import RouteTbl
from utils.requests import request_handler


class CleintConnectionHandler:
    def __init__(self):
        self.reader= None
        self.writer= None
        self.routes_table= None
        self.queues= None

    def add_queues(self, queues:Queues):
        self.queues= queues
    def add_routes(self, routes: RouteTbl):
        self.routes_table= routes.ROUTES


    async def __call__(self, reader:StreamReader, writer:StreamWriter):
        if self.queues is None or self.routes_table is None:
            print(f"\n[SERVER][WARNING] No queues or routes are added!")
            return None
       
        self.reader= reader
        self.writer= writer

        peer_addr= self.writer.get_extra_info('peername')
        ssl_obj= self.writer.get_extra_info('ssl_object')

        print(f"\n[SERVER]: Accepted connection from {peer_addr}")
        print(f"\n[SERVER]: SSL/TLS handhsake is complete. Protocol: {ssl_obj.version()} | Cipher: {ssl_obj.cipher()}")

        buffer= b''

        try:
            while True:
                data= await self.reader.read(4096)
                if not data:
                    break

                buffer += data
                #print(f"\nInitial buffer: {buffer} - buffer_len: {len(buffer)}\n")
                while True:
                    if len(buffer) < 4:
                        break
                    req_params= request_handler(buffer)
                    req_len= next(req_params)
                    req_metadata= next(req_params)
                    route= req_metadata.get('path')
                    method= req_metadata.get('method')

                    new_req= next(req_params)

                    routes_field= self.routes_table[method]

                    if route in routes_field:
                        handler= routes_field[route]
                        task= asyncio.create_task(handler(queue= self.queues, request= new_req))
                        response= await task
                        if response is not None:
                            print(response)
                            try:
                                self.writer.write(response)
                                await self.writer.drain()
                                print(f"[SERVER]: response sent successfully")
                            except Exception as e:
                                print(f'[SERVER]: Could not send the response')
                            

                    else:
                        response= f"[SERVER]: Unrecognisable command {route}"
                        self.writer.write(response.encode('utf-8'))
                        await self.writer.drain()
                    
                    buffer= buffer[4 + req_len:]
                    #print(f"\nFinal buffer: {buffer} - len: {len(buffer)}\n")

        except ConnectionResetError:
            print(f"\n[SERVER]: Client {peer_addr} disconnected unexpectedly")
        except Exception as e:
            print(f"\n[SERVER]: An unexpected error occured: {e}")
    
 
