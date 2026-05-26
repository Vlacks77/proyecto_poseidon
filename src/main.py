# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Inicializamos la aplicación central de FastAPI
app = FastAPI(
    title="Proyecto Poseidón API",
    description="Backend transaccional para el control de inventarios y ventas",
    version="1.0.0"
)

# Configuración básica de CORS (para que tu frontend en Angular pueda conectarse sin bloqueos)
origins = [
    "http://localhost:4200",  # Dirección estándar de desarrollo de Angular
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint de prueba (Ruta raíz) para verificar que el backend responda con éxito
@app.get("/", tags=["Root"])
def read_root():
    return {
        "status": "online",
        "project": "PROYECTO-POSEIDON",
        "message": "Servidor FastAPI inicializado correctamente"
    }

# Dentro de tu src/main.py central:
from src.modules.ventas.router import router as ventas_router
app.include_router(ventas_router, prefix="/api/v1")