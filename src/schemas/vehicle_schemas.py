from pydantic import BaseModel, ConfigDict, field_validator


class VehicleRegisterRequest(BaseModel):
    """Request para registrar un vehículo"""
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


class VehicleResponse(BaseModel):
    """Response con datos de un vehículo"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    matricula: str
    marca: str
    modelo: str
    anio: int
    estado: str


class VehicleDetailResponse(BaseModel):
    """Response detallada con información del dueño"""
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
    """Response con lista de vehículos"""
    vehiculos: list[VehicleDetailResponse]
    total: int