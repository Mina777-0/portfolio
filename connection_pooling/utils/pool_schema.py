import asyncio
from typing import Annotated, Any
from collections import deque
from schemas import RangeValidator
from validators import validate_pool_size



class AsyncPool:
    '''
    This is an async pool with waiting list. Putters and getters can wait for an appointed timeout or cancellation. 
    '''

    pool_capacity: Annotated[int, RangeValidator(min_value=1, max_value=10)]

    def __init__(self, **kw):
        self.pool_capacity= kw.get('pool_capacity') if kw.get('pool_capacity') else 2
        self._queue= set()
        # Getter waiting list
        self._getters= deque()
        # Putter waiting list
        self._putters= deque()

        max_value= validate_pool_size(AsyncPool, self)
        self.max_value= max_value

    # Current queue size
    def psize(self):
        return len(self._queue)

    def pool_connections(self):
        return self._queue
    
    def _clear_connections(self):
        self._queue.clear()
    

    def wakeup_call(self, waiters: deque):
        ''' standard asyncio pattern to wake up the next valid waiter on the waiting list'''
        while waiters:
            waiter= waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)
                break
        


    async def put(self, item: Any):
        # If the pool is full. please Wait!
        while self.psize() >= self.pool_capacity:

            loop= asyncio.get_running_loop()
            # Create a placeholder and add to the waiting list
            waiter= loop.create_future()
            self._putters.append(waiter)

            try:
                response= await waiter
                print(f"putter: {response}")
                print("Stop-11")
                
            except (asyncio.CancelledError, asyncio.TimeoutError) as e:
    
                if self.psize() < self.pool_capacity and not waiter.cancelled():
                    # Wake up the placeholder in the putter waiting list
                    self.wakeup_call(self._putters) 
                    print("Stop-12")
                
                elif self.psize() < self.max_value:
                    self.pool_capacity += 1
                    print(f"Pool size increased: {self.pool_capacity}")
                    self.wakeup_call(self._putters)
                    print("Stop-1e")

                # Cancel the placeholder in the waiting list
                waiter.cancel()
                print("Stop-13")

                
                print("Stop-14")
                raise e

            finally:
                try:
                    if waiter.cancelled():
                        # Clear the waiting list
                        self._putters.remove(waiter)
                except ValueError:
                    pass


                    

        # If the pool still can hold more connections 
        self._queue.add(item)

        # Notify the getter on the waiting list that an item is put 
        self.wakeup_call(self._getters)

        

    async def get(self):
        # If there's no connection in the pool. Please wait!
        while not self._queue:
            loop= asyncio.get_running_loop()
            # Create a placeholder and add to the waiting list
            waiter= loop.create_future()
            self._getters.append(waiter)

            try:
                # If the wakeup-call set result to the place holder, the await will pass and the loop will break.
                response= await waiter
                print(f"getter: {response}")
                print("Stop-21")
                
            except (asyncio.CancelledError, asyncio.TimeoutError) as e:
                if self._queue and not waiter.cancelled():
                    self.wakeup_call(self._getters)
                    print("Stop-22")
                waiter.cancel()
                print("Stop-23")

                
                print("Stop-24")
                
                raise e
            
            finally:
                try:
                    if waiter.cancelled():
                        # Clear the waiting list
                        self._getters.remove(waiter)
                except ValueError:
                    pass 



        # If there are connections in the pool
        item= self._queue.pop()

        # Notify the putter waiting list that a place is available now 
        self.wakeup_call(self._putters)

        return item 
    



class PoolEmptyError(Exception):
    '''Raised when pool is empty to create any session'''
    pass
