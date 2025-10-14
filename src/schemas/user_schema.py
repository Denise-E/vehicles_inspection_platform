from pydantic import BaseModel, EmailStr, constr

# Request schema
class UserRegisterRequest(BaseModel):
    nombre_completo: constr(min_length=3)
    mail: EmailStr
    telefono: constr(min_length=6, max_length=20) | None = None
    password: constr(min_length=6)
    rol_id: int

# Response schema
class UserResponse(BaseModel):
    id: int
    nombre_completo: str
    mail: EmailStr
    telefono: str | None
    rol_id: int
    activo: bool

    class Config:
        orm_mode = True  # Permite convertir objetos SQLAlchemy directamente
