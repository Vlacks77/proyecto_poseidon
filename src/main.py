from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.modules.ventas.router import router as ventas_router
from src.modules.inventario.router import router as inventario_router # NUEVA IMPORTACIÓN

app = FastAPI(
    title="PROYECTO POSEIDON - API CONTABLE",
    description="Backend transaccional de alta precisión para el control de inventarios, suministros y ventas.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración CORS para Angular (Puerto 4200)
origins = [
    "http://localhost:4200",
    "https://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REGISTRO DE ROUTERS VERSIONADOS
app.include_router(ventas_router, prefix="/api/v1")
app.include_router(inventario_router, prefix="/api/v1") # REGISTRO DEL NUEVO ROUTER

@app.get("/", tags=["Root"])
def comprobar_estado_servidor():
    return {
        "status": "ONLINE",
        "sistema": "PROYECTO-POSEIDON",
        "documentacion": "/docs"
    }