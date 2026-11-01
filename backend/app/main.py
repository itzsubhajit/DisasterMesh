
import asyncio

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import (
    initialize_database,
    test_database_connection,
)

from .queue_worker import run_queue_worker

from .routers import (
    alerts,
    analytics,
    auth,
    emergencies,
    gateway,
    logs,
    messages,
    nodes,
    packet_queue,
    routes,
    users,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting DisasterMesh backend...")

    test_database_connection()
    initialize_database()

    # Start the automatic packet queue worker.
    worker_stop_event = asyncio.Event()

    worker_task = asyncio.create_task(
        run_queue_worker(worker_stop_event),
        name="disastermesh-packet-queue-worker",
    )

    print("Automatic packet queue worker started.")
    print("DisasterMesh backend started successfully.")

    try:

        yield

    finally:

        print("Stopping DisasterMesh background services...")

        # Request graceful worker shutdown.
        worker_stop_event.set()

        # Wait until the current processing batch finishes.
        await worker_task

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
app.include_router(messages.router)
app.include_router(emergencies.router)
app.include_router(routes.router)
app.include_router(logs.router)
app.include_router(gateway.router)
app.include_router(packet_queue.router)
app.include_router(alerts.router)
app.include_router(analytics.router)


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
