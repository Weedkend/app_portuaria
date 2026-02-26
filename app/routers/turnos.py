from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/turnos", tags=["Turnos"])

@router.post("/", response_model=schemas.Turno, status_code=status.HTTP_201_CREATED)
def create_turno(turno: schemas.TurnoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo turno"""
    # Verificar que el usuario existe
    db_usuario = crud.get_usuario(db, usuario_id=turno.id_usuario)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar que el camión existe y pertenece al usuario
    db_camion = crud.get_camion(db, camion_id=turno.id_camion)
    if not db_camion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camión no encontrado"
        )
    
    if db_camion.id_usuario != turno.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El camión no pertenece al usuario especificado"
        )
    
    # Validar fechas
    if turno.fecha_fin and turno.fecha_fin <= turno.fecha_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de fin debe ser posterior a la fecha de inicio"
        )
    
    return crud.create_turno(db=db, turno=turno)

@router.get("/", response_model=List[schemas.Turno])
def read_turnos(
    skip: int = 0,
    limit: int = 100,
    usuario_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    camion_id: Optional[int] = Query(None, description="Filtrar por ID de camión"),
    activos: bool = Query(False, description="Mostrar solo turnos activos"),
    db: Session = Depends(get_db)
):
    """Obtener lista de turnos"""
    turnos = crud.get_turnos(
        db, 
        skip=skip, 
        limit=limit, 
        usuario_id=usuario_id,
        camion_id=camion_id,
        activos=activos
    )
    return turnos

@router.get("/{turno_id}", response_model=schemas.TurnoWithRelations)
def read_turno(turno_id: int, db: Session = Depends(get_db)):
    """Obtener un turno por ID con sus relaciones"""
    db_turno = crud.get_turno(db, turno_id=turno_id)
    if db_turno is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turno no encontrado"
        )
    return db_turno

@router.put("/{turno_id}", response_model=schemas.Turno)
def update_turno(
    turno_id: int, 
    turno: schemas.TurnoUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar un turno"""
    # Verificar relaciones si se actualizan
    if turno.id_usuario:
        db_usuario = crud.get_usuario(db, usuario_id=turno.id_usuario)
        if not db_usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
    
    if turno.id_camion:
        db_camion = crud.get_camion(db, camion_id=turno.id_camion)
        if not db_camion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Camión no encontrado"
            )
    
    # Validar fechas si se actualizan
    if turno.fecha_inicio and turno.fecha_fin:
        if turno.fecha_fin <= turno.fecha_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de fin debe ser posterior a la fecha de inicio"
            )
    
    db_turno = crud.update_turno(db, turno_id=turno_id, turno=turno)
    if db_turno is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turno no encontrado"
        )
    return db_turno

@router.delete("/{turno_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_turno(turno_id: int, db: Session = Depends(get_db)):
    """Eliminar un turno"""
    deleted = crud.delete_turno(db, turno_id=turno_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turno no encontrado"
        )
    return None

@router.post("/{turno_id}/finalizar", response_model=schemas.Turno)
def finalizar_turno(
    turno_id: int,
    kilometros: Decimal = Query(..., description="Kilómetros recorridos"),
    db: Session = Depends(get_db)
):
    """Finalizar un turno activo"""
    db_turno = crud.finalizar_turno(db, turno_id=turno_id, kilometros=kilometros)
    if db_turno is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turno no encontrado o ya finalizado"
        )
    return db_turno