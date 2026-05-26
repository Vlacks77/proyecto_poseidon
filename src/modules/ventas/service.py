from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from datetime import datetime, date
from decimal import Decimal

from src.modules.ventas.models import Venta, DetalleVenta, Factura, Cliente
from src.modules.ventas.schemas import ConfirmarVentaIn, FinalizarVentaIn
from src.modules.inventario.models import Stock, Producto, HistorialStock

class VentasService:

    @staticmethod
    def obtener_proximo_id(db: Session, modelo, columna_id: str) -> int:
        """Helper para emular la secuencia de IDs de tu DDL actual"""
        tabla = modelo.__tablename__
        query = db.execute(text(f"SELECT COALESCE(MAX({columna_id}), 0) + 1 FROM public.{tabla}"))
        return query.scalar()

    @classmethod
    def precalcular_resumen_venta(cls, db: Session, payload: ConfirmarVentaIn) -> dict:
        """
        LÓGICA DE NEGOCIO - PASO 1 (CONFIRMAR):
        Simula la venta, valida el stock disponible y calcula subtotales sin alterar la BD.
        """
        subtotal = Decimal('0.000')
        items_validados = []

        # Validar existencia del cliente de antemano
        cliente = db.query(Cliente).filter(Cliente.id == payload.id_cliente).first()
        if not cliente:
            raise HTTPException(status_code=404, detail=f"El cliente con ID {payload.id_cliente} no existe.")

        for item in payload.items:
            # 1. Buscar producto y su stock mapeado
            producto = db.query(Producto).filter(Producto.id_producto == item.id_producto).first()
            if not producto:
                raise HTTPException(status_code=404, detail=f"El producto con ID {item.id_producto} no existe.")
            
            stock = db.query(Stock).filter(Stock.id_producto == item.id_producto).first()
            if not stock:
                raise HTTPException(status_code=404, detail=f"No se encontró registro de inventario para {producto.descripcion}.")

            # 2. Validar existencias rigurosamente según el tipo de medida ('U' o 'K')
            if producto.medida == "U":
                if item.unidades <= 0:
                    raise HTTPException(status_code=400, detail=f"Debe especificar unidades válidas para {producto.descripcion}.")
                if stock.unidades < item.unidades:
                    raise HTTPException(status_code=400, detail=f"Stock insuficiente para {producto.descripcion}. Disponibles: {stock.unidades} U")
                
                # Calcular total de este ítem
                precio_aplicado = producto.precio if producto.precio is not None else producto.precio_sf
                total_item = precio_aplicado * item.unidades
            
            elif producto.medida == "K":
                if item.kilos <= 0:
                    raise HTTPException(status_code=400, detail=f"Debe especificar kilogramos válidos para {producto.descripcion}.")
                if stock.kilos < item.kilos:
                    raise HTTPException(status_code=400, detail=f"Stock insuficiente para {producto.descripcion}. Disponibles: {stock.kilos} Kg")
                
                precio_aplicado = producto.precio if producto.precio is not None else producto.precio_sf
                total_item = (precio_aplicado * item.kilos).quantize(Decimal('0.001'))
            
            else:
                raise HTTPException(status_code=400, detail=f"Tipo de medida inválido para el producto {producto.descripcion}.")

            subtotal += total_item
            items_validados.append({
                "id_producto": item.id_producto,
                "descripcion": producto.descripcion,
                "precio_aplicado": precio_aplicado,
                "unidades": item.unidades,
                "kilos": item.kilos,
                "total": total_item
            })

        total_pagar = subtotal - payload.rebaja
        if total_pagar < 0:
            total_pagar = Decimal('0.000')

        return {
            "subtotal": subtotal,
            "rebaja": payload.rebaja,
            "total_pagar": total_pagar,
            "items_validados": items_validados
        }

    @classmethod
    def ejecutar_finalizar_venta(cls, db: Session, payload: FinalizarVentaIn) -> dict:
        """
        LÓGICA DE NEGOCIO - PASO 2 (FINALIZAR):
        Ejecuta la transacción ACID completa. Descuenta stock, guarda histórico,
        maestro, detalles y genera factura de ser necesario.
        """
        # Volvemos a calcular el resumen en caliente para blindar los montos desde el servidor
        contrato_confirmacion = ConfirmarVentaIn(
            id_cliente=payload.id_cliente,
            items=payload.items,
            rebaja=payload.rebaja,
            tipo_venta=payload.tipo_venta
        )
        resumen = cls.precalcular_resumen_venta(db, contrato_confirmacion)
        total_pagar = resumen["total_pagar"]

        # Validar el dinero entregado por el cliente
        if payload.efectivo_recibido < total_pagar:
            raise HTTPException(
                status_code=400, 
                detail=f"Efectivo insuficiente. Requiere {total_pagar}, recibió {payload.efectivo_recibido}."
            )

        cambio = payload.efectivo_recibido - total_pagar
        ahora = datetime.utcnow()

        try:
            # A. REGISTRAR MAESTRO DE VENTA (vta_ventas)
            id_nueva_venta = cls.obtener_proximo_id(db, Venta, "id_venta")
            nueva_venta = Venta(
                id_venta=id_nueva_venta,
                fecha=date.today(),
                id_cliente=payload.id_cliente,
                rebaja=payload.rebaja,
                tipo=payload.tipo_venta,
                efectivo=payload.efectivo_recibido,
                cambio=cambio,
                fec_cre=ahora,
                usu_cre=payload.usuario,
                api_estado="ACTIVO"
            )
            db.add(nueva_venta)

            # B. PROCESAR DETALLES, ACTUALIZAR STOCK Y GENERAR HISTORIAL
            for item in resumen["items_validados"]:
                # Re-posicionamos las entidades correspondientes para mutarlas
                stock_db = db.query(Stock).filter(Stock.id_producto == item["id_producto"]).with_for_update().first()
                
                # 1. Insertar el Detalle de la Venta (vta_detalle_ventas)
                nuevo_detalle = DetalleVenta(
                    id_venta=id_nueva_venta,
                    id_producto=item["id_producto"],
                    unidades=item["unidades"],
                    kilos=item["kilos"],
                    precio_unitario=item["precio_aplicado"],
                    fec_cre=ahora,
                    usu_cre=payload.usuario,
                    api_estado="ACTIVO"
                )
                db.add(nuevo_detalle)

                # 2. Descontar stock físicamente de la tabla inv_stock
                stock_db.unidades -= item["unidades"]
                stock_db.kilos -= item["kilos"]
                stock_db.fec_mod = ahora
                stock_db.usu_mod = payload.usuario

                # 3. Generar Registro en el Historial de Stock (inv_historial_stock)
                id_nuevo_historial = cls.obtener_proximo_id(db, HistorialStock, "id_inv_historial_stock")
                nuevo_historial = HistorialStock(
                    id_inv_historial_stock=id_nuevo_historial,
                    id_stock=stock_db.id_stock,
                    id_venta=id_nueva_venta,
                    tipo="VENTA",
                    fec_cre=ahora,
                    usu_cre=payload.usuario,
                    api_estado="ACTIVO"
                )
                db.add(nuevo_historial)

            # C. MANEJO DE FACTURACIÓN (vta_facturas)
            if payload.tipo_venta == "CF":
                cliente_db = db.query(Cliente).filter(Cliente.id == payload.id_cliente).first()
                id_nueva_factura = cls.obtener_proximo_id(db, Factura, "id_factura")
                
                nueva_factura = Factura(
                    id_factura=id_nueva_factura,
                    id_cliente=payload.id_cliente,
                    nit=cliente_db.nit,
                    id_venta=id_nueva_venta,
                    fec_cre=ahora,
                    usu_cre=payload.usuario,
                    api_estado="EMITIDO"
                )
                db.add(nueva_factura)

            # EFECTUAR CAMBIOS DEFINITIVOS EN POSTGRES
            db.commit()
            
            return {
                "id_venta": id_nueva_venta,
                "total_pagar": total_pagar,
                "efectivo_recibido": payload.efectivo_recibido,
                "cambio": cambio,
                "fecha_transaccion": ahora
            }

        except Exception as e:
            db.rollback() # Abortamos toda la operación en cascada ante cualquier imprevisto 
            raise HTTPException(
                status_code=500, 
                detail=f"Fallo crítico transaccional en el Servidor: {str(e)}"
            )

    @staticmethod
    def buscar_clientes_por_criterio(db: Session, query: str) -> List[Cliente]:
        """
        Busca clientes por Razón Social o por coincidencia exacta/parcial de su NIT.
        """
        if not query or len(query.strip()) < 2:
            return []

        termino = f"%{query.strip()}%"
        
        # Filtramos si el nombre coincide o si el NIT transformado a texto coincide
        from sqlalchemy import cast, String
        return db.query(Cliente).filter(
            (Cliente.razon_social.ilike(termino)) | 
            (cast(Cliente.nit, String).like(termino))
        ).all()
        