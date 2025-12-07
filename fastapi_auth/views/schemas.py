from pydantic import BaseModel, model_validator, EmailStr, Field, field_validator
from typing import Self
import re 


class SignupSchema(BaseModel):
    email:EmailStr= Field(..., max_length=255)
    first_name:str= Field(..., max_length=64)
    last_name:str= Field(..., max_length=64)
    password1:str= Field(..., min_length=8)
    password2:str= Field(..., min_length=8)
    

    @field_validator('password1')
    @classmethod
    def validate_password_complexity(cls, value):
        PASSWORD_COMPLEXITY= r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%&*]).{8,}$'
        if not re.search(PASSWORD_COMPLEXITY, value):
            raise ValueError("Password is unacceptable")
        #print(value)
        return value
    

    @model_validator(mode='before')
    @classmethod
    def validate_data(cls, data) -> dict:
        if 'fname' in data:
            data['first_name']= data.pop('fname')
        if 'lname' in data:
            data['last_name']= data.pop('lname')

        #print(f"Data: {data}")
        return data 
    
    @model_validator(mode='after')
    def validate_passwords(self) -> Self:
        if self.password1 != self.password2:
            raise ValueError("Passwords don't match")
       
        #print(f"Instance: {self}")
        return self
    

class SinginSchema(BaseModel):
    email:EmailStr= Field(...)
    password:str= Field(...)


class ChangePasswordSchema(BaseModel):
    old_password:str= Field(...)
    new_password1:str= Field(..., min_length=8)
    new_password2:str= Field(..., min_length=8)

    @field_validator('new_password1')
    @classmethod
    def validate_password_complexity(cls, value):
        PASSWORD_COMPLEXITY= r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%&*]).{8,}$'
        if re.search(PASSWORD_COMPLEXITY, value):
            raise ValueError("Password is unacceptable")
        return value
    
    @model_validator(mode='after')
    def validate_passwords(self) -> Self:
        if self.new_password1 != self.new_password2:
            raise ValueError("Passwords don't match")
        return self
    

