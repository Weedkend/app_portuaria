from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List, Optional
from app import models, schemas

# CRUD Usuarios
def get_usuario(db: Session, usuario_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id_usuario == usuario_id).first()

def get_usuario_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()

def create_usuario(db: Session, usuario: schemas.UsuarioCreate):
    db_usuario = models.Usuario(**usuario.model_dump())
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def update_usuario(db: Session, usuario_id: int, usuario: schemas.UsuarioUpdate):
    db_usuario = get_usuario(db, usuario_id)
    if db_usuario:
        update_data = usuario.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_usuario, field, value)
        db.commit()
        db.refresh(db_usuario)
    return db_usuario

def delete_usuario(db: Session, usuario_id: int):
    db_usuario = get_usuario(db, usuario_id)
    if db_usuario:
        db.delete(db_usuario)
        db.commit()
        return True
    return False

# CRUD Camiones
def get_camion(db: Session, camion_id: int):
    return db.query(models.Camion).filter(models.Camion.id_camion == camion_id).first()

def get_camion_by_placa(db: Session, placa: str):
    return db.query(models.Camion).filter(models.Camion.placa == placa).first()

def get_camiones(db: Session, skip: int = 0, limit: int = 100, usuario_id: Optional[int] = None):
    query = db.query(models.Camion)
    if usuario_id:
        query = query.filter(models.Camion.id_usuario == usuario_id)
    return query.offset(skip).limit(limit).all()

def create_camion(db: Session, camion: schemas.CamionCreate):
    db_camion = models.Camion(**camion.model_dump())
    db.add(db_camion)
    db.commit()
    db.refresh(db_camion)
    return db_camion

def update_camion(db: Session, camion_id: int, camion: schemas.CamionUpdate):
    db_camion = get_camion(db, camion_id)
    if db_camion:
        update_data = camion.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_camion, field, value)
        db.commit()
        db.refresh(db_camion)
    return db_camion

def delete_camion(db: Session, camion_id: int):
    db_camion = get_camion(db, camion_id)
    if db_camion:
        db.delete(db_camion)
        db.commit()
        return True
    return False

# CRUD Turnos
def get_turno(db: Session, turno_id: int):
    return db.query(models.Turno).filter(models.Turno.id_turno == turno_id).first()

def get_turnos(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    usuario_id: Optional[int] = None,
    camion_id: Optional[int] = None,
    activos: bool = False
):
    query = db.query(models.Turno)
    
    if usuario_id:
        query = query.filter(models.Turno.id_usuario == usuario_id)
    if camion_id:
        query = query.filter(models.Turno.id_camion == camion_id)
    if activos:
        query = query.filter(models.Turno.fecha_fin == None)
    
    return query.order_by(models.Turno.fecha_inicio.desc()).offset(skip).limit(limit).all()

def create_turno(db: Session, turno: schemas.TurnoCreate):
    db_turno = models.Turno(**turno.model_dump())
    db.add(db_turno)
    db.commit()
    db.refresh(db_turno)
    return db_turno

def update_turno(db: Session, turno_id: int, turno: schemas.TurnoUpdate):
    db_turno = get_turno(db, turno_id)
    if db_turno:
        update_data = turno.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_turno, field, value)
        db.commit()
        db.refresh(db_turno)
    return db_turno

def delete_turno(db: Session, turno_id: int):
    db_turno = get_turno(db, turno_id)
    if db_turno:
        db.delete(db_turno)
        db.commit()
        return True
    return False

def finalizar_turno(db: Session, turno_id: int, kilometros: Decimal):
    db_turno = get_turno(db, turno_id)
    if db_turno and db_turno.fecha_fin is None:
        db_turno.fecha_fin = datetime.now()
        db_turno.kilometros_recorridos = kilometros
        db.commit()
        db.refresh(db_turno)
    return db_turno

# Estadísticas
def get_estadisticas_usuario(db: Session, usuario_id: int):
    from sqlalchemy import func
    
    resultado = db.query(
        models.Usuario.id_usuario,
        models.Usuario.nombre,
        models.Usuario.apellido,
        func.count(func.distinct(models.Camion.id_camion)).label('total_camiones'),
        func.count(func.distinct(models.Turno.id_turno)).label('total_turnos'),
        func.sum(models.Turno.kilometros_recorridos).label('km_totales')
    ).outerjoin(
        models.Camion, models.Usuario.id_usuario == models.Camion.id_usuario
    ).outerjoin(
        models.Turno, models.Usuario.id_usuario == models.Turno.id_usuario
    ).filter(
        models.Usuario.id_usuario == usuario_id
    ).group_by(
        models.Usuario.id_usuario
    ).first()
    
    return resultado