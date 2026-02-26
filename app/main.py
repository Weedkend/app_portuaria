from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import usuarios, camiones, turnos
from app.database import engine, Base

# Crear las tablas en la base de datos (solo para desarrollo)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Gestión de Flota de Camiones",
    description="API para gestionar usuarios, camiones y turnos",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(usuarios.router)
app.include_router(camiones.router)
app.include_router(turnos.router)

@app.get("/")
async def root():
    return {
        "message": "API de Gestión de Flota de Camiones",
        "version": "1.0.0",
        "endpoints": {
            "usuarios": "/usuarios",
            "camiones": "/camiones",
            "turnos": "/turnos",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}