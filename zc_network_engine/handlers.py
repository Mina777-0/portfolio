import socket, ssl, os, sys, asyncio, time 
from dotenv import load_dotenv
from urllib.parse import urlparse
from typing import Optional
import struct

load_dotenv('.ven')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
#print(sys.path)

from utils.buffers_schemas import CircularBuffer


password= os.environ.get('PASSWORD')
#print(password, type(password))
password_bytes= bytes(password, encoding='utf-8')


cert_file= os.path.abspath(os.path.join(os.path.dirname(__file__), 'cert.pem'))
key_file= os.path.abspath(os.path.join(os.path.dirname(__file__), 'key.pem'))


class SocketHandler:
    def __init__(self):
        self.ssock: Optional[socket.socket]= None
        self.loop= asyncio.get_running_loop()
        self.cb= CircularBuffer(65535)
    

    def connect(self, host:str, port:int):
        
        context= ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

        try:
            context.load_cert_chain(certfile=cert_file, keyfile=key_file, password=password_bytes)
        except FileNotFoundError as e:
            raise e
        

        sock= socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            sock.bind((host, port))
            sock.listen(1)
            print(f"\n[SERVER]: Server is listening on {host}:{port}")

            conn, addr= sock.accept()
            print(f"\n[SERVER]: Unencrypted connection to {addr}")

            self.ssock= context.wrap_socket(conn, server_side= True) 
            print(f"\n[SERVER]: SSL Handshake is complete. Protocol: {self.ssock.version()}")
            #print(f"\n[SERVER]: Secure connection is established with {addr}")

            

        except ConnectionResetError as e:
            raise e 
        except BrokenPipeError as e:
            raise e 
        except Exception as e:
            raise e 
        
    async def handle_connection(self):
        if self.ssock is None:
            print(f"\n[SERVER]: Connection is closed or unestablished.")
            return 
        
        try:
            
            self.ssock.setblocking(False)
            
            while True:
                try:
                    t0= time.perf_counter_ns()
                    # used loop.sock_recv_into the TLS send encrypted data the socket cannot decrypt
                    #nbytes= await self.loop.sock_recv_into(self.ssock, buffer)

                    # We use the native recv_into. This performs decryption in-place into the buffer
                    nbytes= self.ssock.recv_into(self.cb.write_to())

                    if nbytes == 0:
                        break
                    self.cb.did_write(nbytes)

                    while self.cb.count >= self.cb.PACKET_SIZE:
                        #print(self.cb.peek())
                        fields= struct.unpack('!IddQ', self.cb.peek())
                        #print(fields)

                        self.cb.advance()
                    
                    t1= time.perf_counter_ns()
                    print(f"\n[TIME PROCESSOR]: {(t1 - t0) / 1000 :2f} microseconds")

                except (ssl.SSLWantWriteError, ssl.SSLWantReadError):
                    # IF the socket is empty, wait for it to be ready again
                    # We yield control back to the loop to talk to the epoll or kqueue of the kernel unitl the FD is ready
                    
                    waiter= self.loop.create_future()
                    fd= self.ssock.fileno()
                    
                    self.loop.add_reader(fd, lambda: waiter.done() or waiter.set_result(None))
                    try:
                        await waiter
                    finally:
                        self.loop.remove_reader(fd)
                    continue

            

        except ConnectionAbortedError:
            raise
        except Exception as e:
            
            raise e
        
        