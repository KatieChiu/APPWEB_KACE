from dataclasses import dataclass
from models.Persona import Persona
from models.Ubicacion import Ubicacion

@dataclass
class Cliente(Persona, Ubicacion):
    ClienteID: int
    direccion: Ubicacion #uno a uno



