from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime


# Request schemas
class InspectionCreateRequest(BaseModel):
    """Schema para crear una inspección asociada a un turno"""
    turno_id: int
    inspector_id: int


class ChequeoRequest(BaseModel):
    """Schema para un chequeo individual"""
    item_numero: int = Field(..., ge=1, le=8, description="Número del item chequeado (1-8)")
    descripcion: str = Field(..., min_length=3, max_length=200, description="Descripción del chequeo")
    puntuacion: int = Field(..., ge=1, le=10, description="Puntuación del chequeo (1-10)")
    
    @field_validator('puntuacion')
    @classmethod
    def validate_puntuacion(cls, v: int) -> int:
        if v < 1 or v > 10:
            raise ValueError('La puntuación debe estar entre 1 y 10')
        return v
    
    @field_validator('item_numero')
    @classmethod
    def validate_item_numero(cls, v: int) -> int:
        if v < 1 or v > 8:
            raise ValueError('El número de item debe estar entre 1 y 8')
        return v


class ChequeosListRequest(BaseModel):
    """Schema para registrar la lista de 8 chequeos"""
    chequeos: list[ChequeoRequest] = Field(..., min_length=8, max_length=8)
    
    @field_validator('chequeos')
    @classmethod
    def validate_exactly_8_chequeos(cls, v: list[ChequeoRequest]) -> list[ChequeoRequest]:
        if len(v) != 8:
            raise ValueError('Debe proporcionar exactamente 8 chequeos')
        
        # Verificar que no haya items duplicados
        items = [chequeo.item_numero for chequeo in v]
        if len(items) != len(set(items)):
            raise ValueError('No puede haber items duplicados')
        
        # Verificar que los items sean del 1 al 8
        if set(items) != {1, 2, 3, 4, 5, 6, 7, 8}:
            raise ValueError('Los items deben ser del 1 al 8 sin omitir ninguno')
        
        return v


class InspectionCloseRequest(BaseModel):
    """Schema para cerrar una inspección (opcional: incluir observación)"""
    observacion: str | None = Field(None, min_length=10, max_length=500)


# Response schemas
class ChequeoResponse(BaseModel):
    """Schema de respuesta para un chequeo"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    item_numero: int
    descripcion: str
    puntuacion: int
    fecha: datetime


class InspectionResponse(BaseModel):
    """Schema de respuesta para una inspección"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    turno_id: int
    vehiculo_matricula: str
    inspector_nombre: str
    fecha: datetime
    puntuacion_total: int
    resultado: str | None
    observacion: str | None
    estado: str


class InspectionDetailResponse(BaseModel):
    """Schema de respuesta detallada para una inspección con sus chequeos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    turno_id: int
    vehiculo_matricula: str
    inspector_nombre: str
    fecha: datetime
    puntuacion_total: int
    resultado: str | None
    observacion: str | None
    estado: str
    chequeos: list[ChequeoResponse]


class InspectionListResponse(BaseModel):
    """Schema de respuesta para listar inspecciones"""
    inspecciones: list[InspectionResponse]
    total: int

