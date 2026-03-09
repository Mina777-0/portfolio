import socket, ssl, asyncio, os, sys, struct
from typing import Optional
from urllib.parse import urlparse


cert_file= os.path.abspath(os.path.join(os.path.dirname(__file__), 'cert.pem'))
key_file= os.path.abspath(os.path.join(os.path.dirname(__file__), 'key.pem'))


class CreateConnection:
    def __init__(self):
        self.ssock: Optional[socket.socket]= None

    async def open_connection(self, url: str):
        try:
            uri= urlparse(url)

            username= uri.username
            password= uri.password

            host= uri.hostname
            port= uri.port if uri.port else 2547

        except Exception as e:
            print(f"\n[CLIENT]: Error in parsing the url: {e}")

        
        context= ssl.create_default_context()
        context.check_hostname= False
        context.verify_mode= ssl.CERT_REQUIRED

        try:
            context.load_verify_locations(cert_file)
            #print(f"\n[CLIENT]: 'cert.pem' is found")
        except FileNotFoundError as e:
            #print(f"\n[CLIENT]: 'cert.pem' is missing")
            raise e

        try:
            sock= socket.socket(family=socket.AF_INET, type= socket.SOCK_STREAM)
            self.ssock= context.wrap_socket(sock, server_hostname= host)
            #print(f"socket is wrapped")

            self.ssock.connect((host, port))
            print(f"\n[CLIENT]: SSL/TLS Handshake is successful with {host}:{port}. Protocol: {self.ssock.version()}")


        except ConnectionError:
            raise
        except BrokenPipeError:
            raise
        except Exception as e:
            print(f"\n[CLIENT]: Unexpected error occured: {e}")
        
    async def send_packets(self):
        if self.ssock is None:
            print(f"\n[CLIENT]: Socket is closed or none")
            return
        
        i= 0

        try:
            while True:
                print(i)
                self.ssock.sendall(
                    struct.pack(
                        '!IddQ',
                        1001,
                        150.25,
                        150.30,
                        500
                    )
                )

                i +=1


        except Exception as e:
            print(f"\n[CLIENT]: Error in sending packets: {e}")
        finally:
            self.ssock.close()



