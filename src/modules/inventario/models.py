from sqlalchemy import Column, Integer, String, DateTime, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.config.database import Base

class Producto(Base):
    __tablename__ = 'productos'

    id_producto = Column(Integer, primary_key=True, nullable=False)
    descripcion = Column(String, nullable=False)
    marca = Column(String)
    precio = Column(Numeric(6, 3))
    medida = Column(String(10), nullable=False)  # 'U' o 'K'
    precio_sf = Column(Numeric(6, 3))

    # Auditoría
    fec_cre = Column(DateTime, default=datetime.utcnow)
    fec_mod = Column(DateTime, onupdate=datetime.utcnow)
    usu_cre = Column(String(50))
    usu_mod = Column(String(50))
    api_estado = Column(String(20), default='ACTIVO')
    api_transaccion = Column(String(20))

    stock = relationship("Stock", uselist=False, back_populates="producto")


class Stock(Base):
    __tablename__ = 'inv_stock'

    id_stock = Column(Integer, primary_key=True, nullable=False)
    id_producto = Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    unidades = Column(Integer, nullable=False, default=0)
    kilos = Column(Integer, nullable=False, default=0)

    # Auditoría
    fec_cre = Column(DateTime, default=datetime.utcnow)
    fec_mod = Column(DateTime, onupdate=datetime.utcnow)
    usu_cre = Column(String(50))
    usu_mod = Column(String(50))
    api_estado = Column(String(20), default='ACTIVO')
    api_transaccion = Column(String(20))

    producto = relationship("Producto", back_populates="stock")
    historiales = relationship("HistorialStock", back_populates="stock")


class HistorialStock(Base):
    __tablename__ = 'inv_historial_stock'

    id_inv_historial_stock = Column(Integer, primary_key=True, nullable=False)
    id_stock = Column(Integer, ForeignKey('inv_stock.id_stock'), nullable=False)
    id_inv_suministro = Column(Integer, ForeignKey('inv_suministro.id'), nullable=True)
    id_venta = Column(Integer, ForeignKey('vta_ventas.id_venta'), nullable=True)
    tipo = Column(String)  # 'VENTA', 'INGRESO', etc.

    # Auditoría
    fec_cre = Column(DateTime, default=datetime.utcnow)
    fec_mod = Column(DateTime, onupdate=datetime.utcnow)
    usu_cre = Column(String(50))
    usu_mod = Column(String(50))
    api_estado = Column(String(20), default='ACTIVO')
    api_transaccion = Column(String(20))

    stock = relationship("Stock", back_populates="historiales")
    venta = relationship("Venta")  # Relación cruzada al módulo de ventas