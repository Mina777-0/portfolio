from typing import Annotated, Set, Tuple, Optional, Self
from asyncio import StreamReader, StreamWriter
import asyncio, json, ssl
from contextlib import asynccontextmanager
import os, sys 
from urllib.parse import urlparse


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.schemas import RangeValidator, Unit
from utils.validators import validate_pool_size




class AsyncPool:

    pool_size: Annotated[int, RangeValidator(min_value=1, max_value=10, exclusive=True)]
    pool_timeout: Annotated[float, Unit(name="seconds")]
    pool_recycle: Annotated[float, Unit(name="seconds")]


    def __init__(self, url:str, **kw):
        #self.reader:Optional[StreamReader]= None
        #self.writer:Optional[StreamWriter]= None

        self.uri= url
        self.host= None
        self.port= None

        self.pool: Set[Tuple[StreamReader, StreamWriter]]= set()
        self.pool_size= kw.get('pool_size') if kw else 3
        self.pool_recycle= kw.get('pool_recycle') if kw else 20.0
        self.pool_timeout= kw.get('pool_timeout') if kw else 30.0

        
        self.pool_lock= asyncio.Lock()
        self.pool_is_ready= asyncio.Event()
        self.recycled_task:Optional[asyncio.Task]= None


        # Validate the size of the pool with the range
        try:
            self.pool_size= validate_pool_size(AsyncPool, self)

            print(f"\n[CONNECTION POOL]: pool size: {self.pool_size}")
        except Exception as e:
            print(f"\n[CONNECTION POOL]: ERROR: {e}")
    
    # Start the connection pool
    async def start(self):
        self.uri_config()

        #await self.add_to_pool()
        try:
            await self._open_connection_and_to_pool()
        except Exception as e:
            print(f"\n[CONNECTION POOL]: ERROR in opening connection: {e}")

        # Pool is ready 
        self.pool_is_ready.set()

        if self.recycled_task is None or self.recycled_task.done():
            self.recycled_task= asyncio.create_task(self.run_recycler())
        
        print(f"\n[CONNECTION POOL]: Pool is ready: pool-size: {len(self.pool)}")

        #return self.pool


    # Close the connection pool
    async def close(self):
        if self.recycled_task:
            self.recycled_task.cancel()
            try:
                await self.recycled_task
            except asyncio.CancelledError:
                pass 
        

        closed_tasks=[]
        async with self.pool_lock:
            for reader, writer in list(self.pool):
                if not writer.is_closing():
                    writer.close()
                    closed_tasks.append(writer.wait_closed())
            
            if closed_tasks:
                await asyncio.gather(*closed_tasks, return_exceptions=True)

            self.pool.clear()
            print(f"\n[CONNECTION POOL]: All connections are closed")



    def uri_config(self):
        # Uri config
        if not self.uri:
            print(f"\n[CLIENT]: URL is not found")
            return
        
        parsed_uri= urlparse(self.uri, scheme="aesbus")

        if not parsed_uri:
            print(f"\n[CLIENT]: Provided url is unrecognised")
            return 
        
        self.host= parsed_uri.hostname
        self.port= parsed_uri.port if parsed_uri else 2547

        if parsed_uri.username != 'guest' or parsed_uri.password != 'guest':
            print(f"\n[CLIENT]: The username or password provided in the uri is not recognised")
            return


    async def _open_connection_and_to_pool(self):
        new_connections_buffer=[]

        # Open secure connection
        context= ssl.create_default_context()
        context.check_hostname= False
        context.verify_mode= ssl.CERT_REQUIRED

        try:
            context.load_verify_locations('cert1.pem')
        except FileNotFoundError:
            print(f"\n[CLIENT]: 'cert1.pem is missing")
        for i in range(self.pool_size):
            try:
                reader, writer= await asyncio.open_connection(
                    host= self.host,
                    port= self.port,
                    ssl= context,
                    server_hostname= self.host,
                    ssl_handshake_timeout= 10.0
                )

                #self.reader= reader
                #self.writer= writer

                peer_addr= writer.get_extra_info('peername')
                ssl_obj= writer.get_extra_info('ssl_object')
                print(f"\n[CLIENT]: Connection opened with {peer_addr}")
                print(f"\n[CLIENT]: SSL/TLS handhsake is successful. Protocol: {ssl_obj.version()} | Cipher: {ssl_obj.cipher()}")

                new_connections_buffer.append((reader, writer))

                if reader is None or writer is None:
                    print(f"\n[CLIENT]: Cannot read or write")
                    return
                
                message= {
                    'method': 'PING',
                    'body': f"Connection {i+1} is established"
                }

                writer.write(json.dumps(message).encode('utf-8'))
                await writer.drain()

                data= await reader.read(1024)
                print(data.decode('utf-8'))

                #return (reader, writer)
        
            except ConnectionError:
                print(f"\n[CLIENT]: Connection failed. Is the server running?")
            except Exception as e:
                print(f"\n[CLIENT]: Unexpected error occured: {e}")

        # Add the connections to the pool
        async with self.pool_lock:
            if new_connections_buffer:
                for conn in new_connections_buffer:
                    reader, writer= conn
                    self.pool.add(conn)
                    print(f"\n[CONNECTION POOL]: Connection {writer.get_extra_info('sockname')} entered the pool")
            
            print(f"\n[CONNECTION POOL]: Pool is filled. Pool-size: {len(self.pool)}")




    # Add connections to the pool as long as the conns less than the max_value
    '''
    async def add_to_pool(self):
        async with self.pool_lock:
            connection_list= []

            if len(self.pool) < self.pool_size:
                required_conns= self.pool_size - len(self.pool)
                for _ in range(required_conns):
                    connection_list.append(self._open_connection())

            
            if connection_list:
                results= await asyncio.gather(*connection_list)
                new_connections= [connection for connection in results if connection is not None]
                self.pool.update(new_connections)
                print(f"\n[CONNECTION POOL]: Pool is ready. Pool size: {len(self.pool)}")
    '''
    
    # Recycle the pool
    async def run_recycler(self):  
        #closed_connections=0      
        while True:

            await asyncio.sleep(self.pool_recycle)

            async with self.pool_lock:

                for reader, writer in list(self.pool):
                    if not writer.is_closing():
                        print(f"\n[CONNECTION POOL]: Connection {writer.get_extra_info('sockname')} is closing")
                        try:
                            writer.close()
                            await writer.wait_closed()
                            #closed_connections +=1
                            # Remove the connection
                            self.pool.remove((reader, writer))
                            print(f"\n[CONNECTION POOL]: Pool size: {len(self.pool)}")

                        except Exception as e:
                            print(f"\n[CONNECTION POOL]: ERROR in closing connection: {e}")

            # Open new connections
            await self._open_connection_and_to_pool()
            print(f"\n[RECYLCE]: Pool is recycled")


    @asynccontextmanager
    async def create_session(self):
        connection_session: Tuple[StreamReader, StreamWriter]= None

        await self.pool_is_ready.wait()

        async with self.pool_lock:
            if self.pool:
                connection_session= self.pool.pop()
                print(f"\n[CONNECTION POOL]: Connection is borrowed from the pool. Pool size: {len(self.pool)}")
            else:
                # We can add more connections to the pool as long as the size is less than the max after waiting for timeout
                await asyncio.sleep(self.pool_timeout)
                if self.pool:
                    connection_session= self.pool.pop()
                else:
                    pass
                    # Add to the pool 
                print(f"\n[CONNECTIN POOL]: Pool is empty. No connection found")

        reader, writer= connection_session

        if reader.at_eof() or writer.is_closing():
            print(f"[CONNECTION POOL]: Connection session is lost")
            try:
                writer.close()
                await writer.wait_closed()
            except ConnectionError:
                pass 
        else:
            try:
                yield reader, writer
            except Exception as e:
                print(f"\n[CONNECTION POOL]: ERROR: {e}")
            
            else:
                async with self.pool_lock:
                    self.pool.add(connection_session)
                    print(f"\n[CONNECTION POOL]: Connection returned to the pool. Pool size: {len(self.pool)}")


            
                
                    





        


    
  
