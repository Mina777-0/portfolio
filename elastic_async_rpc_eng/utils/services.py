from typing import Dict, Callable, Awaitable, Any
import psutil, os 

class ServiceRouter:
    Router: Dict[str, Callable]= {}


    @classmethod
    def serivce(cls, method: str):
        def wrapper(f: Callable):
            if method not in cls.Router:
                cls.Router[method]= f
                return f 
        return wrapper
    

service_router= ServiceRouter()
#print(service_router.Router)

@service_router.serivce('add')
def addition(*args):
    return args[0] + args[1]


@service_router.serivce('multi')
def multiplication(*args):
    return args[0] * args[1]


#print(service_router.Router)

# This service is special for the server health ** need to import psutil library that looks for system resources
@service_router.serivce('server.stat')
def get_health(*args):
    process= psutil.Process(os.getpid())

    active_queues= args[0]
    status= ""

    if active_queues < 4:
        status= "Healthy"
    else:
        status= "Degrading"

    return {
        'status': status,
        'memeory_usage_mb': process.memory_info().rss / (1024 * 1024),
        'cpu_usage_percentage': psutil.cpu_percent(),
        'active queues': args[0]
    }


