from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional

class ProductoStockOut(BaseModel):
    id_producto: int = Field(..., description="ID único del producto")
    descripcion: str = Field(..., description="Nombre o descripción del artículo")
    marca: Optional[str] = Field(None, description="Marca del producto")
    precio: Optional[Decimal] = Field(None, max_digits=6, decimal_places=3, description="Precio Con Factura")
    precio_sf: Optional[Decimal] = Field(None, max_digits=6, decimal_places=3, description="Precio Sin Factura")
    medida: str = Field(..., description="U = Unidades, K = Kilogramos")
    unidades_disponibles: int = Field(..., description="Stock físico actual en piezas")
    kilos_disponibles: Decimal = Field(..., max_digits=6, decimal_places=3, description="Stock físico actual en Kg")

    class Config:
        from_attributes = True