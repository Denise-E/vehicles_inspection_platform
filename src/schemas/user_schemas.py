from pydantic import BaseModel, EmailStr, constr, ConfigDict

# Request schemas
class UserRegisterRequest(BaseModel):
    nombre_completo: constr(min_length=3)
    mail: EmailStr
    telefono: constr(min_length=6, max_length=20) 
    contrasenia: constr(min_length=6)
    rol: str

class UserLoginRequest(BaseModel):
    mail: EmailStr
    contrasenia: constr(min_length=6)

# Response schema
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nombre_completo: str
    mail: EmailStr
    telefono: str 
    rol: str
    activo: bool


class UserLoginResponse(BaseModel):
    id: int
    nombre_completo: str
    mail: EmailStr
    telefono: str
    rol: str
    activo: bool
    token: str