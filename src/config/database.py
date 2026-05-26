# src/config/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Define la cadena de conexión a tu PostgreSQL local
# Cambia 'usuario', 'contraseña' y 'nombre_base_datos' por tus datos reales de Postgres/DBeaver
DATABASE_URL = "postgresql://postgres:123@localhost:5432/scp"

# 2. El Engine es el encargado de comunicarse directamente con el driver de la BD
engine = create_engine(DATABASE_URL)

# 3. SessionLocal será la fábrica de sesiones de base de datos para nuestras peticiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Clase base de la cual heredarán todos nuestros modelos ORM (ventas, inventario, etc.)
Base = declarative_base()

# 5. Función/Dependencia para obtener la sesión de la BD en cada endpoint y cerrarla al terminar
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()