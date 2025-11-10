from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional


class VehicleRegisterRequest(BaseModel):
    duenio_id: int
    matricula: str
    marca: str
    modelo: str
    anio: int
    
    @field_validator('anio')
    @classmethod
    def validate_anio(cls, v: int) -> int:
        if v < 1900 or v > 2100:
            raise ValueError('El año debe estar entre 1900 y 2100')
        return v


class VehicleUpdateRequest(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    
    @field_validator('anio')
    @classmethod
    def validate_anio(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1900 or v > 2100):
            raise ValueError('El año debe estar entre 1900 y 2100')
        return v
    
    def model_post_init(self, __context):
        """Valida que al menos un campo haya sido proporcionado"""
        if self.marca is None and self.modelo is None and self.anio is None:
            raise ValueError('Debe proporcionar al menos un campo para actualizar')


class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matricula: str
    marca: str
    modelo: str
    anio: int
    estado: str


class VehicleDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matricula: str
    marca: str
    modelo: str
    anio: int
    estado: str
    duenio_id: int
    nombre_duenio: str


class VehicleListResponse(BaseModel):
    vehiculos: list[VehicleDetailResponse]
    total: int