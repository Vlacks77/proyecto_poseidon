from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# =====================================================================
# 1. ESQUEMAS DE DETALLE (Estructura interna de los productos a vender)
# =====================================================================

class ItemVentaBase(BaseModel):
    id_producto: int = Field(..., gt=0, description="ID único del producto")
    unidades: Optional[int] = Field(default=0, ge=0, description="Cantidad en piezas")
    kilos: Optional[Decimal] = Field(default=Decimal('0.000'), ge=0, max_digits=6, decimal_places=3, description="Cantidad en kilogramos")

    @field_validator('unidades', 'kilos')
    def validar_cantidades_positivas(cls, v):
        # Impedimos valores negativos de raíz
        if v is not None and v < 0:
            raise ValueError("La cantidad no puede ser negativa")
        return v


# =====================================================================
# 2. ESQUEMAS DE ENTRADA (Lo que Angular envía al Backend)
# =====================================================================

class ConfirmarVentaIn(BaseModel):
    """Contrato para calcular el resumen de la compra en el Modal"""
    id_cliente: int = Field(..., gt=0, description="ID del cliente comprador")
    items: List[ItemVentaBase] = Field(..., min_items=1, description="Lista de productos seleccionados")
    rebaja: Optional[Decimal] = Field(default=Decimal('0.000'), ge=0, max_digits=6, decimal_places=3)
    tipo_venta: str = Field(..., description="SF = Sin Factura, CF = Con Factura")

    @field_validator('tipo_venta')
    def validar_tipo_venta(cls, v):
        if v not in ['SF', 'CF']:
            raise ValueError("El tipo de venta debe ser 'SF' (Sin Factura) o 'CF' (Con Factura)")
        return v


class FinalizarVentaIn(BaseModel):
    """Contrato final para efectuar la transacción y cobro"""
    id_cliente: int = Field(..., gt=0)
    items: List[ItemVentaBase] = Field(..., min_items=1)
    rebaja: Decimal = Field(..., ge=0, max_digits=6, decimal_places=3)
    tipo_venta: str
    efectivo_recibido: Decimal = Field(..., ge=0, max_digits=6, decimal_places=3)
    usuario: str = Field(default="sys_user", min_length=3, max_length=50)

    @field_validator('tipo_venta')
    def validar_tipo_venta(cls, v):
        if v not in ['SF', 'CF']:
            raise ValueError("El tipo de venta debe ser 'SF' o 'CF'")
        return v


# =====================================================================
# 3. ESQUEMAS DE SALIDA (Lo que el Backend responde de forma segura)
# =====================================================================

class ItemValidadoOut(BaseModel):
    id_producto: int
    descripcion: str
    precio_aplicado: Decimal
    unidades: int
    kilos: Decimal
    total: Decimal

    class Config:
        from_attributes = True


class ResumenVentaOut(BaseModel):
    """Estructura de respuesta que Angular renderizará en el resumen de compra"""
    subtotal: Decimal
    rebaja: Decimal
    total_pagar: Decimal
    items_validados: List[ItemValidadoOut]

    class Config:
        from_attributes = True


class FinalizarVentaOut(BaseModel):
    """Respuesta al cerrar exitosamente la caja"""
    status: str = Field(default="VENTA_PROCESADA_EXITOSAMENTE")
    id_venta: int
    total_pagar: Decimal
    efectivo_recibido: Decimal
    cambio: Decimal
    fecha_transaccion: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True