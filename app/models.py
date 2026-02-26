from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class EstadoCamion(str, enum.Enum):
    disponible = "disponible"
    en_ruta = "en_ruta"
    mantenimiento = "mantenimiento"
    inactivo = "inactivo"

class TipoTurno(str, enum.Enum):
    mañana = "mañana"
    tarde = "tarde"
    noche = "noche"

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telefono = Column(String(20))
    fecha_registro = Column(DateTime, server_default=func.current_timestamp())
    activo = Column(Boolean, default=True)

    # Relaciones
    camiones = relationship("Camion", back_populates="usuario", cascade="all, delete-orphan")
    turnos = relationship("Turno", back_populates="usuario", cascade="all, delete-orphan")

class Camion(Base):
    __tablename__ = "camiones"

    id_camion = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    placa = Column(String(20), unique=True, nullable=False, index=True)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50))
    capacidad_toneladas = Column(DECIMAL(10, 2))
    año_fabricacion = Column(Integer)
    estado = Column(Enum(EstadoCamion), default=EstadoCamion.disponible)
    fecha_registro = Column(DateTime, server_default=func.current_timestamp())

    # Relaciones
    usuario = relationship("Usuario", back_populates="camiones")
    turnos = relationship("Turno", back_populates="camion", cascade="all, delete-orphan")

class Turno(Base):
    __tablename__ = "turnos"
    __table_args__ = (
        CheckConstraint('fecha_fin IS NULL OR fecha_fin > fecha_inicio', name='chk_fechas'),
    )

    id_turno = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    id_camion = Column(Integer, ForeignKey("camiones.id_camion", ondelete="CASCADE"), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=True)
    tipo_turno = Column(Enum(TipoTurno), nullable=False)
    kilometros_recorridos = Column(DECIMAL(10, 2))
    observaciones = Column(Text)
    fecha_registro = Column(DateTime, server_default=func.current_timestamp())

    # Relaciones
    usuario = relationship("Usuario", back_populates="turnos")
    camion = relationship("Camion", back_populates="turnos")