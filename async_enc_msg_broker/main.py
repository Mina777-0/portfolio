from app import create_app
import asyncio
import ssl
from dotenv import load_dotenv
import os, sys 


load_dotenv('.env')
password= os.environ.get('PASSWORD')
password_bytes= bytes(password, encoding='utf-8')

app= create_app()

async def run_server():
    global password_bytes, app
    context= ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    try:
        context.load_cert_chain(certfile='cert.pem', keyfile='key.pem', password=password_bytes)
    except FileNotFoundError:
        print(f"\n[SERVER]: 'cert.pem' or 'key.pem' is missing")
        return
    
    try:

        server= await asyncio.start_server(
            lambda r,w: app(r,w),
            host= "127.0.0.1",
            port= 2547,
            ssl= context
        )
        
        server_addr= server.sockets[0].getsockname()
        print(f"[SERVER]: secure server is running on {server_addr}. Waiting for connection ...")

        async with server:
            await server.serve_forever()

    except asyncio.TimeoutError:
        print(f"\n[SERVER]: Handshake failed.")
    except Exception as e:
        print(f"\n[SERVER]: An unexpected error occured")





if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print(f"Application is closed")