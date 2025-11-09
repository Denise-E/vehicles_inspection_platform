from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional


# Request schemas
class DisponibilidadRequest(BaseModel):
    """Request para consultar disponibilidad de turnos del sistema"""
    fecha_inicio: Optional[str] = None  # Formato: "YYYY-MM-DD", si no se envía usa hoy
    fecha_final: Optional[str] = None  # Formato: "YYYY-MM-DD", opcional para consultar rango
    
    @field_validator('fecha_inicio', 'fecha_final')
    @classmethod
    def validate_fecha_format(cls, v: Optional[str]) -> Optional[str]:
        if v:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v
    
    def validate_fecha_range(self):
        """Valida que fecha_final sea posterior a fecha_inicio"""
        if self.fecha_inicio and self.fecha_final:
            inicio = datetime.strptime(self.fecha_inicio, '%Y-%m-%d')
            final = datetime.strptime(self.fecha_final, '%Y-%m-%d')
            if final < inicio:
                raise ValueError('fecha_final debe ser posterior a fecha_inicio')
        return True


class BookingCreateRequest(BaseModel):
    """Request para crear un turno"""
    matricula: str
    fecha: str  # Formato: "YYYY-MM-DD HH:MM"
    
    @field_validator('fecha')
    @classmethod
    def validate_fecha_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, '%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD HH:MM')
        return v


class BookingUpdateRequest(BaseModel):
    """Request para actualizar el estado de un turno"""
    estado_id: int
    
    @field_validator('estado_id')
    @classmethod
    def validate_estado_id(cls, v: int) -> int:
        # Validar que el estado_id sea uno de los válidos: 1-RESERVADO, 2-CONFIRMADO, 3-COMPLETADO, 4-CANCELADO
        if v not in [1, 2, 3, 4]:
            raise ValueError('estado_id inválido. Debe ser 1 (RESERVADO), 2 (CONFIRMADO), 3 (COMPLETADO) o 4 (CANCELADO)')
        return v


# Response schemas
class SlotDisponible(BaseModel):
    """Representa un slot de tiempo disponible"""
    fecha: str  # Formato: "YYYY-MM-DD HH:MM"
    disponible: bool


class DisponibilidadResponse(BaseModel):
    """Response con slots disponibles del sistema"""
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

