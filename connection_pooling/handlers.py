import asyncio
from asyncio import StreamReader, StreamWriter
import json 
from typing import Optional



class ConnectionHandler:
    def __init__(self):
        self.reader:Optional[StreamReader]= None
        self.writer:Optional[StreamWriter]= None


    async def __call__(self, reader:StreamReader, writer:StreamWriter):
        
        self.reader= reader
        self.writer= writer

        peer_addr= self.writer.get_extra_info('peername')
        ssl_obj= self.writer.get_extra_info('ssl_object')

        print(f"\n[SERVER]: Accepted conenction from {peer_addr}")
        print(f"\n[SERVER]: SSL/TLS handshake is established. Protocol: {ssl_obj.version()} | Cipher: {ssl_obj.cipher()}")

        if self.reader is None or self.writer is None:
            print(f"\n[SERVER]: Cannot read or write data")
            return None
        
        try:
            while True:
                data= await self.reader.read(1024)
                if not data:
                    break
                try:
                    message= json.loads(data.decode('utf-8'))
                except json.JSONDecodeError:
                    print(f"\n[SERVER]: Error in decoding the incoming data")
                
                if message.get('method')== 'PING': 
                    writer.write('Hello-Secure-World'.encode('utf-8'))
                    await writer.drain()
                
                else:
                    writer.write('Your request is received'.encode('utf-8'))
                    await writer.drain()

                print(message.get('body'))


        except ConnectionResetError:
            print(f"\n[SERVER]: {peer_addr} has disrupted the connection")
        except BrokenPipeError as e:
            print(f"\n[SERVER]: ERROR: {e}")
        except asyncio.TimeoutError:
            print(f"\n[SERVER]: Timeout: {e}")
        except Exception as e:
            print(f"\n[SERVER]: An unexpected error occured: {e}")
        finally:
            if not writer.is_closing():
                writer.close()
                await writer.wait_closed()
