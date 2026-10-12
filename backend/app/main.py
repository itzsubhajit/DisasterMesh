from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import initialize_database, test_database_connection
from .routers import (
    auth,
    emergencies,
    gateway,
    logs,
    messages,
    nodes,
    routes,
    users,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting DisasterMesh backend...")
    test_database_connection()
    initialize_database()
    print("DisasterMesh backend started successfully.")
    yield
    print("DisasterMesh backend shutting down...")


app = FastAPI(
    title="DisasterMesh API",
    description=(
        "Backend API for the DisasterMesh emergency communication "
        "and rescue coordination system."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(nodes.router)
app.include_router(messages.router)
app.include_router(emergencies.router)
app.include_router(routes.router)
app.include_router(logs.router)
app.include_router(gateway.router)


@app.get("/")
def root():
    return {
        "project": "DisasterMesh",
        "status": "online",
        "message": "DisasterMesh backend is running.",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "DisasterMesh Backend",
    }


@app.get("/api/system/status")
def system_status():
    return {
        "system": "DisasterMesh",
        "backend": "online",
        "database": "connected",
        "status": "operational",
    }