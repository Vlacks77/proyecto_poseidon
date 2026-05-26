from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.config.database import get_db  # Dependencia para el ciclo de vida de la sesión SQL
from src.modules.ventas.schemas import ConfirmarVentaIn, ResumenVentaOut, FinalizarVentaIn, FinalizarVentaOut
from src.modules.ventas.service import VentasService

router = APIRouter(
    prefix="/ventas",
    tags=["Módulo de Ventas y Facturación"]
)

@router.post(
    "/confirmar", 
    response_model=ResumenVentaOut, 
    status_code=status.HTTP_200_OK,
    summary="Precalcula subtotales y valida disponibilidad de inventario"
)
def confirmar_resumen_venta(payload: ConfirmarVentaIn, db: Session = Depends(get_db)):
    """
    ### Endpoint de Simulación e Idempotencia:
    Invoca este endpoint cuando el usuario haga clic en **'Confirmar Venta'** dentro del modal de Angular.
    
    - **No altera el estado de la base de datos**.
    - Verifica de forma estricta que haya stock físico disponible (en Unidades o Kilos).
    - Retorna el subtotal, la rebaja aplicada y el neto final calculado de manera segura en el servidor.
    """
    # Delegamos toda la carga conceptual a la capa de negocio
    resumen_calculado = VentasService.precalcular_resumen_venta(db=db, payload=payload)
    return resumen_calculado


@router.post(
    "/finalizar", 
    response_model=FinalizarVentaOut, 
    status_code=status.HTTP_201_CREATED,
    summary="Ejecuta la venta de forma atómica y descuenta inventario"
)
def finalizar_transaccion_venta(payload: FinalizarVentaIn, db: Session = Depends(get_db)):
    """
    ### Endpoint de Cierre de Caja (Transaccional ACID):
    Invoca este endpoint únicamente cuando el usuario presione **'Finalizar Venta'** tras recibir el efectivo.
    
    - Registra la cabecera en `vta_ventas`.
    - Inserta los productos desglosados en `vta_detalle_ventas`.
    - Afecta en caliente las existencias en `inv_stock` bloqueando filas de forma segura.
    - Impacta la bitácora histórica en `inv_historial_stock`.
    - Genera la factura en `vta_facturas` si el parámetro `tipo_venta` es igual a **'CF'** (Con Factura).
    - Calcula el cambio exacto a entregar al cliente.
    """
    # Orquestamos la transacción en el servicio
    resultado_transaccion = VentasService.ejecutar_finalizar_venta(db=db, payload=payload)
    return resultado_transaccion