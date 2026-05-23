from fastapi import FastAPI

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="Sistema de Inventarios y Ventas",
    description="API para el manejo de inventario, ventas y reportes",
    version="1.0.0"
)

# Creamos un endpoint de prueba (Ruta raíz)
@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido al Sistema de Inventario bb"}

# Endpoint para simular la obtención de productos
@app.get("/productos")
def get_productos():
    return [
        {"id": 1, "nombre": "Laptop", "stock": 15, "precio": 800.00},
        {"id": 2, "nombre": "Mouse", "stock": 50, "precio": 25.00}
    ]
