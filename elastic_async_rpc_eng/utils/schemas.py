from typing import Annotated, get_args
from dataclasses import dataclass, field
import inspect
from uuid import uuid4 

@dataclass
class Unit:
    name: str
    abbrevaition: str | None= None



# Json-rpc message structure 
@dataclass
class RpcMessage:
    id: str= field(default_factory= lambda:uuid4().hex)
    method: str= ""
    params: list | None = field(default_factory= list)
    jsonrpc: str= "2.0"

    '''
    If a standard JSON-RPC library is used on either end later, they will reject your messages if the keys are capitalized.
    '''
    def request_data(self):
        return {
            'jsonrpc': self.jsonrpc,
            'id': self.id,
            'method': self.method,
            'params': self.params
            }
        


# Here we inherit from Exception. It does know how to handle. We can use __init__ if we want to add logic like queue name or something

class QueueFullError(Exception):
    '''Raised when the queue is full and the timeout is reached'''
    pass 

class QueueNameError(Exception):
    '''Raised when a requested queue name does not exists or is invalid'''
    pass 

class QueueEmptyError(Exception):
    '''Raised when the requested queue is empty'''
    pass 


class PublishJobError(Exception):
    '''Raised when writer cannot send messages'''
    pass 


class QueueCreationError(Exception):
    '''Rasied when the total number of queues is met'''
    pass 

