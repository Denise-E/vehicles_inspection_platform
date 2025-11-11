from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime


# Request schemas
class ChequeoRequest(BaseModel):
    descripcion: str = Field(..., max_length=200, description="Descripción del chequeo")
    puntuacion: int = Field(..., ge=1, le=10, description="Puntuación del chequeo (1-10)")
    
    @field_validator('puntuacion')
    @classmethod
    def validate_puntuacion(cls, v: int) -> int:
        if v < 1 or v > 10:
            raise ValueError('La puntuación debe estar entre 1 y 10')
        return v


class InspectionCreateRequest(BaseModel):
    turno_id: int
    inspector_id: int
    chequeos: list[ChequeoRequest] = Field(..., min_length=8, max_length=8, description="Los 8 chequeos de la inspección")
    observacion: str | None = Field(None, min_length=10, max_length=500, description="Observación sobre la inspección (obligatoria si resultado es RECHEQUEAR)")
    
    @field_validator('chequeos')
    @classmethod
    def validate_chequeos(cls, v: list[ChequeoRequest]) -> list[ChequeoRequest]:
        if len(v) != 8:
            raise ValueError('Debe proporcionar exactamente 8 chequeos')
        
        return v


# Response schemas (ChequeoResponse, InspectionDetailResponse, InspectionListResponse)
class ChequeoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    descripcion: str
    puntuacion: int
    fecha: datetime


class InspectionResponse(BaseModel):
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
    inspecciones: list[InspectionResponse]
    total: int

