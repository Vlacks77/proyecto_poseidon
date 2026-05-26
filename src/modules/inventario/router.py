from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from src.config.database import get_db
from src.modules.inventario.schemas import ProductoStockOut
from src.modules.inventario.service import InventarioService

router = APIRouter(
    prefix="/inventario",
    tags=["Módulo de Inventario y Catálogo"]
)

@router.get(
    "/buscar-productos", 
    response_model=List[ProductoStockOut],
    status_code=status.HTTP_200_OK,
    summary="Buscador interactivo de productos con stock para el modal de Angular"
)
def buscar_productos_con_stock(query: str, db: Session = Depends(get_db)):
    """
    Endpoints de consulta reactiva. 
    Angular debe disparar este endpoint a medida que el usuario escribe en el input de búsqueda.
    """
    return InventarioService.buscar_productos_catalogo(db=db, query=query)