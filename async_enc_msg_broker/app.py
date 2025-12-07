import os
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'server')))

from utils.queues import Queues
from server.handlers import router
from server.handle_connection import CleintConnectionHandler



def create_app():
    app= CleintConnectionHandler()

    app.add_queues(Queues())
    app.add_routes(router)

    return app



