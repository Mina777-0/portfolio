from dataclasses import dataclass
import inspect
from typing import get_args, Annotated, Self


@dataclass
class RangeValidator:
    '''
    exclusive range is the difference between the highest and lowest values but the highest not included 
    1-10 the exlusive range is 10 - 1 = 9. so the values are 1 to 9. The lowest value included but not the highest
    '''
    min_value:int 
    max_value:int 
    exclusive: bool= False

    def validate_parameters(self, value: int) -> Self:
        if value < self.min_value or value > self.max_value:
            raise ValueError("Value is out of range")
        
        if self.exclusive:
            if value == self.max_value:
                raise ValueError("The value should be less than max-value or exclusive is False")
            
            self.max_value = self.max_value - self.min_value

        return self 

    
    

@dataclass
class Unit:
    name:str
    abbreviation: str | None
