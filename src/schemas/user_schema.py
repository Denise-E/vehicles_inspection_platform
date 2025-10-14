from pydantic import BaseModel, EmailStr, constr, ConfigDict

# Request schema
class UserRegisterRequest(BaseModel):
    nombre_completo: constr(min_length=3)
    mail: EmailStr
    telefono: constr(min_length=6, max_length=20) | None = None
    password: constr(min_length=6)
    rol_id: int

# Response schema
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nombre_completo: str
    mail: EmailStr
    telefono: str | None
    rol_id: int
    activo: bool
