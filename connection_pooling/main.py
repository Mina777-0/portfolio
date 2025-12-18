import asyncio, ssl 
import sys, os 
from handlers import ConnectionHandler

HOST= "127.0.0.1"


async def run_server():
    global Password

    context= ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    
    try:
        context.load_cert_chain(certfile='cert1.pem', keyfile='key1.pem', password=Password)
    except FileNotFoundError:
        print(f"\n[SERVER]: 'cert1.pem' or 'key1.pem' is not found")

    connection_handler= ConnectionHandler()

    try:
        server= await asyncio.start_server(
            lambda r,w: connection_handler(r,w),
            host= HOST,
            port=2547,
            ssl= context
        )

        server_addr= server.sockets[0].getsockname()
        print(f"\n[SERVER]: Secure server is running on {server_addr}. Waiting for connection ..")


        async with server:
            await server.serve_forever()

    except asyncio.TimeoutError as e:
        print(f"\n[SERVER]: Handshake failed: {e}")  
    except Exception as e:
        print(f"\n[SERVER]: Unexpected error occured: {e}")    
