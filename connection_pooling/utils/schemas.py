from dataclasses import dataclass
import inspect
from typing import get_args, Annotated


@dataclass
class RangeValidator:
    '''
    exclusive range is the difference between the highest and lowest values but the highest not included 
    1-10 the exlusive range is 10 - 1 = 9. so the values are 1 to 9. The lowest value included but not the highest
    '''
    min_value:int 
    max_value:int 
    exclusive: bool= False

    def __post_init__(self):
        if self.exclusive == True:
            self.max_value= self.max_value - self.min_value
    
    

@dataclass
class Unit:
    name:str
    abbreviation: str | None
