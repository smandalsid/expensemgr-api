from pydantic import BaseModel, EmailStr, field_validator
import re

# base class for user
class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str = "98XXXXXX76"

# class to take input while creating user
class CreateUser(UserBase):    
    password: str
    retyped_password: str
    
    @field_validator("username")
    def validate_username(cls, value: str) -> str:
        if len(value)<5:
            raise ValueError("Username must be at least 5 characters long")
        return value
    
    @field_validator("phone_number")
    def validation_phone_number(cls, value: str) -> str:
        pattern = re.compile(r"^\d{10}$")
        if not pattern.match(value):
            raise ValueError("Phone number is not valid")
        return value
    
# class for input while login
class UserLogin(BaseModel):
    username: str
    password: str
    
# class for output
class UserOut(UserBase):
    is_admin: bool
