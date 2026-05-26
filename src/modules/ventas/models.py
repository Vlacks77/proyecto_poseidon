from sqlalchemy import Column, Integer, String, DateTime, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.config.database import Base  # Asumiendo que aquí defines tu Base = declarative_base()

class Venta(Base):
    __tablename__ = 'vta_ventas'

    id_venta = Column(Integer, primary_key=True, nullable=False)
    fecha = Column(Date, nullable=False)
    id_cliente = Column(Integer, ForeignKey('vta_cliente.id'), nullable=False)
    rebaja = Column(Numeric(6, 3), default=0.000)
    tipo = Column(String(2), nullable=True)  # 'SF' o 'CF'
    efectivo = Column(Numeric(6, 3), nullable=True)
    cambio = Column(Numeric(6, 3), nullable=True)
    
    # Columnas de auditoría obligatorias solicitadas
    fec_cre = Column(DateTime, default=datetime.utcnow)
    fec_mod = Column(DateTime, onupdate=datetime.utcnow)
    usu_cre = Column(String(50))
    usu_mod = Column(String(50))
    api_estado = Column(String(20), default='ACTIVO')
    api_transaccion = Column(String(20))

    # Relaciones del ORM (Para cargar datos anidados fácilmente)
    cliente = relationship("Cliente", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")
    facturas = relationship("Factura", back_populates="venta")
    historiales_stock = relationship("HistorialStock", back_populates="venta")


class DetalleVenta(Base):
    """
    ¡La tabla corregida y mandatoria! 
    Mapea la relación Maestro-Detalle de los productos comprados.
    """
    __tablename__ = 'vta_detalle_ventas'

    id_detalle_venta = Column(Integer, primary_key=True, autoincrement=True)
    id_venta = Column(Integer, ForeignKey('vta_ventas.id_venta'), nullable=False)
    id_producto = Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    unidades = Column(Integer, default=0)
    kilos = Column(Integer, default=0)
    precio_unitario = Column(Numeric(6, 3), nullable=False)

    # Auditoría
    fec_cre = Column(DateTime, default=datetime.utcnow)
    fec_mod = Column(DateTime, onupdate=datetime.utcnow)
    usu_cre = Column(String(50))
    usu_mod = Column(String(50))
    api_estado = Column(String(20), default='ACTIVO')
    api_transaccion = Column(String(20))

    # Relaciones
    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto")  # Asume relación con el módulo de inventario


class Cliente(Base):
    __tablename__ = 'vta_cliente'

    id = Column(Integer, primary_key=True, nullable=False)
    razon_social = Column(String, nullable=False)
    celular = Column(Integer)
    nit = Column(Integer)

    # Auditoría
    fec_cre = Column(DateTime, default=datetime.utcnow)
    fec_mod = Column(DateTime, onupdate=datetime.utcnow)
    usu_cre = Column(String(50))
    usu_mod = Column(String(50))
    api_estado = Column(String(20), default='ACTIVO')
    api_transaccion = Column(String(20))

    ventas = relationship("Venta", back_populates="cliente")


class Factura(Base):
    __tablename__ = 'vta_facturas'

    id_factura = Column(Integer, primary_key=True, nullable=False)
    id_cliente = Column(Integer, ForeignKey('vta_cliente.id'), nullable=False)
    nit = Column(Integer)
    id_venta = Column(Integer, ForeignKey('vta_ventas.id_venta'), nullable=True)

    # Auditoría
    fec_cre = Column(DateTime, default=datetime.utcnow)
    fec_mod = Column(DateTime, onupdate=datetime.utcnow)
    usu_cre = Column(String(50))
    usu_mod = Column(String(50))
    api_estado = Column(String(20), default='ACTIVO')
    api_transaccion = Column(String(20))

    venta = relationship("Venta", back_populates="facturas")