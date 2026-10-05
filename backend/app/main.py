from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import initialize_database, test_database_connection
from .routers import auth, nodes, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

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


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(nodes.router)


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "project": "DisasterMesh",
        "status": "online",
        "message": "DisasterMesh backend is running.",
    }


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "DisasterMesh Backend",
    }


# ---------------------------------------------------------
# System status endpoint
# ---------------------------------------------------------

@app.get("/api/system/status")
def system_status():
    return {
        "system": "DisasterMesh",
        "backend": "online",
        "database": "connected",
        "status": "operational",
    }