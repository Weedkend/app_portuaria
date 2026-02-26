from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from enum import Enum

# Enums para Pydantic
class EstadoCamionEnum(str, Enum):
    disponible = "disponible"
    en_ruta = "en_ruta"
    mantenimiento = "mantenimiento"
    inactivo = "inactivo"

class TipoTurnoEnum(str, Enum):
    mañana = "mañana"
    tarde = "tarde"
    noche = "noche"

# Schemas de Usuario
class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=20)
    activo: Optional[bool] = True

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)
    activo: Optional[bool] = None

class Usuario(UsuarioBase):
    id_usuario: int
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)

# Schemas de Camion
class CamionBase(BaseModel):
    id_usuario: int
    placa: str = Field(..., min_length=6, max_length=20, pattern="^[A-Z0-9-]+$")
    marca: str = Field(..., min_length=2, max_length=50)
    modelo: Optional[str] = Field(None, max_length=50)
    capacidad_toneladas: Optional[Decimal] = None
    año_fabricacion: Optional[int] = Field(None, ge=1900, le=datetime.now().year)
    estado: EstadoCamionEnum = EstadoCamionEnum.disponible

class CamionCreate(CamionBase):
    pass

class CamionUpdate(BaseModel):
    id_usuario: Optional[int] = None
    placa: Optional[str] = Field(None, min_length=6, max_length=20, pattern="^[A-Z0-9-]+$")
    marca: Optional[str] = Field(None, min_length=2, max_length=50)
    modelo: Optional[str] = Field(None, max_length=50)
    capacidad_toneladas: Optional[Decimal] = None
    año_fabricacion: Optional[int] = Field(None, ge=1900, le=datetime.now().year)
    estado: Optional[EstadoCamionEnum] = None

class Camion(CamionBase):
    id_camion: int
    fecha_registro: datetime
    usuario: Optional[Usuario] = None

    model_config = ConfigDict(from_attributes=True)

# Schemas de Turno
class TurnoBase(BaseModel):
    id_usuario: int
    id_camion: int
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    tipo_turno: TipoTurnoEnum
    kilometros_recorridos: Optional[Decimal] = None
    observaciones: Optional[str] = None

class TurnoCreate(TurnoBase):
    pass

class TurnoUpdate(BaseModel):
    id_usuario: Optional[int] = None
    id_camion: Optional[int] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    tipo_turno: Optional[TipoTurnoEnum] = None
    kilometros_recorridos: Optional[Decimal] = None
    observaciones: Optional[str] = None

class Turno(TurnoBase):
    id_turno: int
    fecha_registro: datetime
    usuario: Optional[Usuario] = None
    camion: Optional[Camion] = None

    model_config = ConfigDict(from_attributes=True)

# Schemas para respuestas con relaciones
class UsuarioWithRelations(Usuario):
    camiones: List[Camion] = []
    turnos: List[Turno] = []

class CamionWithRelations(Camion):
    turnos: List[Turno] = []

class TurnoWithRelations(Turno):
    pass