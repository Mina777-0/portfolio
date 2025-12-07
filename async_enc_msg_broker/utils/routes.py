from functools import wraps
from typing import Callable, Awaitable, Any, Dict
from asyncio.streams import StreamReader, StreamWriter
import sys, os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from queues import Queues


class RouteTbl:
    ROUTES: Dict[str, Dict[str, Callable[..., Awaitable[None]]]]= {}
    
    @classmethod
    def publish(cls, path:str):
        def reader_wrapper(f:Callable[..., Awaitable[Any]]):
            cls.ROUTES.setdefault('publish', {})

            if path not in cls.ROUTES['publish']:
                print(f"Warning! Overwriting handler for path {path}")
                cls.ROUTES['publish'][path]= f
            return f
        return reader_wrapper


    @classmethod
    def consume(cls, path: str):
        def reader_wrapper(f:Callable[..., Awaitable[Any]]):
            cls.ROUTES.setdefault('consume', {})

            if path not in cls.ROUTES['consume']:
                print(f"Warning! Overwriting handler for path {path}")
                cls.ROUTES['consume'][path]= f
            return f
        return reader_wrapper
    
    @classmethod
    def add_scheduler(cls, path:str):
        def reader_wrapper(f:Callable[..., Awaitable[Any]]):
            cls.ROUTES.setdefault('add_scheduler', {})
            if path not in cls.ROUTES['add_scheduler']:
                cls.ROUTES['add_scheduler'][path]= f
                return f
        return reader_wrapper
    
    @classmethod
    def get_scheduler(cls, path:str):
        def reader_wrapper(f:Callable[..., Awaitable[Any]]):
            cls.ROUTES.setdefault('get_scheduler', {})
            if path not in cls.ROUTES['get_scheduler']:
                cls.ROUTES['get_scheduler'][path]= f
                return f
        return reader_wrapper
    

    





