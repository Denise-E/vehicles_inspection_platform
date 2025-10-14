"""
Este archivo centraliza las importaciones de todos los modelos del sistema.
Permite que se puedan importar fácilmente desde cualquier módulo del proyecto,
sin necesidad de conocer el archivo exacto donde está definido cada modelo.
"""

from src.models.user_model import Usuario
from src.models.vehicle_model import Vehiculo
from src.models.booking_model import Turno
from src.models.inspection_model import Inspeccion
from src.models.chequeo_model import Chequeo

from src.models.user_rol_model import UsuarioRol
from src.models.booking_state_model import EstadoTurno
from src.models.inspection_result_model import ResultadoInspeccion
from src.models.vehicle_state_model import EstadoVehiculo
