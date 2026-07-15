from pydantic import BaseModel , ConfigDict , EmailStr , Field

class LoginRequest(BaseModel):
    email:EmailStr
    password:str