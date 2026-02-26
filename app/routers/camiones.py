from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/camiones", tags=["Camiones"])

@router.post("/", response_model=schemas.Camion, status_code=status.HTTP_201_CREATED)
def create_camion(camion: schemas.CamionCreate, db: Session = Depends(get_db)):
    """Crear un nuevo camión"""
    # Verificar que el usuario existe
    db_usuario = crud.get_usuario(db, usuario_id=camion.id_usuario)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar que la placa no esté registrada
    db_camion = crud.get_camion_by_placa(db, placa=camion.placa)
    if db_camion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La placa ya está registrada"
        )
    
    return crud.create_camion(db=db, camion=camion)

@router.get("/", response_model=List[schemas.Camion])
def read_camiones(
    skip: int = 0, 
    limit: int = 100, 
    usuario_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    db: Session = Depends(get_db)
):
    """Obtener lista de camiones"""
    camiones = crud.get_camiones(db, skip=skip, limit=limit, usuario_id=usuario_id)
    return camiones

@router.get("/{camion_id}", response_model=schemas.CamionWithRelations)
def read_camion(camion_id: int, db: Session = Depends(get_db)):
    """Obtener un camión por ID con sus relaciones"""
    db_camion = crud.get_camion(db, camion_id=camion_id)
    if db_camion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camión no encontrado"
        )
    return db_camion

@router.put("/{camion_id}", response_model=schemas.Camion)
def update_camion(
    camion_id: int, 
    camion: schemas.CamionUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar un camión"""
    # Si se actualiza el id_usuario, verificar que existe
    if camion.id_usuario:
        db_usuario = crud.get_usuario(db, usuario_id=camion.id_usuario)
        if not db_usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
    
    db_camion = crud.update_camion(db, camion_id=camion_id, camion=camion)
    if db_camion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camión no encontrado"
        )
    return db_camion

@router.delete("/{camion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camion(camion_id: int, db: Session = Depends(get_db)):
    """Eliminar un camión"""
    deleted = crud.delete_camion(db, camion_id=camion_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camión no encontrado"
        )
    return None