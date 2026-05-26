from sqlalchemy.orm import Session
from src.modules.inventario.models import Producto, Stock
from typing import List

class InventarioService:

    @staticmethod
    def buscar_productos_catalogo(db: Session, query: str) -> List[dict]:
        """
        Busca productos por descripción o marca filtrando mediante ILIKE (no sensible a mayúsculas)
        y acoplando su stock actual.
        """
        # Exigimos un mínimo de caracteres para no saturar la base de datos si mandan un string vacío
        if not query or len(query.strip()) < 2:
            return []

        termino = f"%{query.strip()}%"
        
        # Realizamos el INNER JOIN entre Producto y Stock
        resultados = db.query(Producto, Stock).\
            join(Stock, Producto.id_producto == Stock.id_producto).\
            filter(Producto.descripcion.ilike(termino) | Producto.marca.ilike(termino)).\
            all()

        # Parseamos la tupla (Producto, Stock) al diccionario que espera el esquema de Pydantic
        catalogo = []
        for producto, stock in resultados:
            catalogo.append({
                "id_producto": producto.id_producto,
                "descripcion": producto.descripcion,
                "marca": producto.marca,
                "precio": producto.precio,
                "precio_sf": producto.precio_sf,
                "medida": producto.medida,
                "unidades_disponibles": stock.unidades,
                "kilos_disponibles": stock.kilos
            })
            
        return catalogo