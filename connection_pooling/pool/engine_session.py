from typing import Annotated, Set, Tuple, Optional, Self
from asyncio import StreamReader, StreamWriter
import asyncio, json, ssl
from contextlib import asynccontextmanager
import os, sys 
from urllib import parse 


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.schemas import RangeValidator, Unit
from utils.validators import validate_pool_size
from utils.pool_schema import AsyncPool, PoolEmptyError



class ClientConnection:
    
    Session: Tuple[StreamReader, StreamWriter]

    def __init__(self, url: str, **kw):
        
        self.pool= AsyncPool()
        self.timeout: float= kw.get('pool_timeout') if kw else 20.0
        self.pool_size: int= kw.get('pool_size') if kw else 2
        self.url= url
        self.pool_lock= asyncio.Lock()
        self.Session= None
        self.pool_recycle: float= kw.get('pool_recycle') if kw else 30.0
        self.recycling_task: asyncio.Task= None



    async def initiate_connection(self):
        uri= parse.urlparse(self.url, scheme= "ssss")

        if not uri:
            print(f"\n[CLIENT]: URL is not provided")
            return None
        

        hostname= uri.hostname
        port= uri.port if uri.port else 2547

        try:
            reader, writer= await asyncio.open_connection(
                host= hostname,
                port= port
            )
            
            server_addr= writer.get_extra_info('peername')
            print(f"\n[CLIENT]: Connection establised with server on {server_addr}")

            return (reader, writer)


        except ConnectionError as e:
            print(f"\n[CLIENT]: Connection failed. Is the server running?")
        except Exception as e:
            print(f"\n[CLIENT]: Unexpected error occured: {e}")

    
    async def add_connections_to_pool(self):

        for _ in range(self.pool.pool_capacity):
            conn= await self.initiate_connection()
            
            conn_addr= conn[1].get_extra_info('sockname')
            

            shakehand_req= {
                'method': 'PING',
                'body': "Hello server"
            }

            conn[1].write(json.dumps(shakehand_req).encode('utf-8'))
            await conn[1].drain()


            data= await conn[0].read(1024)
            if not data:
                raise ConnectionError

            message= data.decode('utf-8')
            print(message)

            print(f"\n[POOL]: {conn_addr} joined the pool")
            #connections_list.append(conn)

            async with self.pool_lock:
                try:
                    await asyncio.wait_for(self.pool.put(conn), timeout= self.timeout)
                    print(f"\n[POOL]: Pool size: {self.pool.psize()}")
                
                except asyncio.TimeoutError as e:
                    print(f"\n[POOL]: Adding connections to the pool failed: {e}")


    async def recycle_pool_connections(self):
        recycled_connections=[]
        closed_connectinos=[]
        

        while True:
            await asyncio.sleep(self.pool_recycle)
            print(f"\n[POOL]: Pool recycling started")

            async with self.pool_lock:
                # Get all the connections in the pool 
                try:
                    for i in range(self.pool.psize()):
                        connection= await asyncio.wait_for(self.pool.get(), timeout=self.timeout)
                        print(f"\n[POOL]: Connectinon-{i+1} is removed from the pool")
                        recycled_connections.append(connection)

                except asyncio.TimeoutError:
                    raise PoolEmptyError(f"\n[POOL]: No connections found")
                
                self.pool._clear_connections()
                print(f"\n[POOL]: Pool is clear of all connections")
                
            for reader, writer in recycled_connections:
                if not writer.is_closing():
                    writer.close()
                    closed_connectinos.append(writer.wait_closed())
                
            await asyncio.gather(*closed_connectinos)

            # Reinitiate connections 
            await self.add_connections_to_pool()
            print(f"\n[POOL]: Pool recycling finished. Waiting for sessions ..")
            



    @asynccontextmanager
    async def create_session(self):
        async with self.pool_lock:

            try:
                self.Session= await asyncio.wait_for(self.pool.get(), timeout= self.timeout)
                print(f"\n[POOL]: Connection is borrowed from the pool. Pool size: {self.pool.psize()}")

            except asyncio.TimeoutError as e:
                raise PoolEmptyError(f"[SESSION MANAGER]: Pool is empty of connections")
                #print(f"\n[SESSION MANAGER]: ERROR: {e}")
            
        reader, writer= self.Session

        addr= writer.get_extra_info('sockname')

        if reader.at_eof() or writer.is_closing():
            print(f"\n[SESSION MANGER]: Session is closing with {addr}")
            try:
                writer.close()
                await writer.wait_closed()

            except Exception as e:
                print(f"\n[SESSION MANAGER]: Error: {e}")
        

        else:
            try:
                yield reader, writer 
            except Exception as e:
                print(f"\n[SESSION MANAGER]: ERROR: {e}")
            else:
                '''
                That's the reason why session-3 or any other additional sessions can't borrow. Because since session-3 hold the lock from get() above,
                sessions 1&2 can't access the lock here to return the connection to the pool. It waits until the time out, then it releases the lock
                and the connections return to the pool
                '''
                #async with self.pool_lock:
                try:
                    
                    await asyncio.wait_for(self.pool.put((reader, writer)), timeout= self.timeout)
                    print(f"\n[SESSION MANAGER]: Connection returned to the pool. Pool size: {self.pool.psize()}")

                except asyncio.TimeoutError as e:
                    print(f"[SESSION MANAGER]: Timeout error: {e}")
        

    
    async def __aenter__(self):
        await self.add_connections_to_pool()

        if self.recycling_task is None:
            self.recycling_task= asyncio.create_task(self.recycle_pool_connections())

        return self
    

    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        closed_connections=[]
        if self.pool:
            for reader, writer in list(self.pool.pool_connections()):
                if not writer.is_closing():
                    writer.close()
                    closed_connections.append(writer.wait_closed())
            
            await asyncio.gather(*closed_connections)
            print(f"\n[POOL]: Connections are closed")
        
        async with self.pool_lock:
            self.pool._clear_connections()
            print(f"\n[POOL]: Pool is cleared. Pool size: {self.pool.psize()}")

        # Clear the lifecycle of zombie-tasks
        if self.recycling_task is not None and not self.recycling_task.cancelled():
            self.recycling_task.cancel()

            try:
                await self.recycling_task
            except asyncio.CancelledError:
                pass 
        





            
                
                    





        


    
  
