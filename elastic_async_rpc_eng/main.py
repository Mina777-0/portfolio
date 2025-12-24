import sys, os, asyncio, ssl 
from asyncio import StreamReader, StreamWriter
from dotenv import load_dotenv
#from app import run_app, ready_to_shutdown

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'server')))

from server.conn_handler import ConnectionHandler
from server.job_handler import WorkersManager
from utils.queues import QueueManager
from utils.services import service_router


load_dotenv('.env')
password= os.environ.get('PASSWORD')
password_bytes= bytes(password, encoding='utf-8')




async def run_server():
    global password_bytes

    # Initialise the app lifecycle
    # Initialise queue
    qm= QueueManager()
    qm.initialise_queue()
    

    # Initialise workers and add queue manager and service router instances
    wm= WorkersManager(qm)
    wm.add_service_router(service_router)
    await wm.start_processes()

    # Initialise the app
    app= ConnectionHandler()
    app.add_queues(qm)
    
    #app= await run_app()

    context= ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    try:
        context.load_cert_chain(certfile= 'cert.pem', keyfile='key.pem', password=password_bytes)
    except FileNotFoundError:
        print(f"\n[SERVER]: 'cert.epm' or 'key.pem' is not found")
    
    try:
        server= await asyncio.start_server(
            lambda r,w: app(r,w),
            host= '127.0.0.1',
            port= 2547,
            ssl= context
        )

        addr= server.sockets[0].getsockname()
        print(f"\n[SERVER]: Server is running on {addr}. Waiting for connection ... ")

        async with server:
            await server.serve_forever()

    
    except ConnectionResetError as e:
        print(f"\n[SERVER]: Connection failed. User reset connection")
    except BrokenPipeError as e:
        print(f"\n[SERVER]: Connection failed. Pipe is broken: {e}")
    except Exception as e:
        print(f"\n[SERVER]: Unexpected error occured: {e}")
    
    finally:
         if wm:
            await wm.close_worker()
    



if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print(f"\n[SERVER]: Error: server is crashed by keyboard interruption")
