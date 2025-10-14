from pydantic import BaseModel, ConfigDict


class VehicleRegisterRequest(BaseModel):
    matricula: str
    marca: str
    modelo: str
    anio: int

class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matricula: str
    marca: str
    modelo: str
    anio: int
    estado: str