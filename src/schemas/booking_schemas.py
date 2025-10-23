from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional


# Request schemas
class DisponibilidadRequest(BaseModel):
    """Request para consultar disponibilidad de turnos"""
    matricula: str
    fecha_inicio: Optional[str] = None  # Formato: "YYYY-MM-DD", si no se envía usa hoy
    
    @field_validator('fecha_inicio')
    @classmethod
    def validate_fecha_format(cls, v: Optional[str]) -> Optional[str]:
        if v:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v


class BookingCreateRequest(BaseModel):
    """Request para crear/reservar un turno"""
    matricula: str
    fecha: str  # Formato: "YYYY-MM-DD HH:MM"
    creado_por: int  # user_id del que crea el turno
    
    @field_validator('fecha')
    @classmethod
    def validate_fecha_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, '%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD HH:MM')
        return v


# Response schemas
class SlotDisponible(BaseModel):
    """Representa un slot de tiempo disponible"""
    fecha: str  # Formato: "YYYY-MM-DD HH:MM"
    disponible: bool


class DisponibilidadResponse(BaseModel):
    """Response con slots disponibles"""
    matricula: str
    slots: list[SlotDisponible]
    total_disponibles: int


class BookingResponse(BaseModel):
    """Response con datos de un turno"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    vehiculo_id: int
    matricula: str
    fecha: str
    estado: str
    creado_por: int
    nombre_creador: str


class BookingListResponse(BaseModel):
    """Response con lista de turnos"""
    turnos: list[BookingResponse]
    total: int

