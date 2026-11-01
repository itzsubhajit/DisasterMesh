
"""
DisasterMesh - Automatic Packet Queue Worker

Periodically checks the persistent packet queue and
synchronizes eligible packets into the main message database.
"""

import asyncio
import logging

from .database import SessionLocal
from .routers.packet_queue import process_queue_batch


logger = logging.getLogger("disastermesh.packet_worker")

# Worker configuration
QUEUE_POLL_INTERVAL_SECONDS = 10
QUEUE_BATCH_SIZE = 25


def process_due_packets():
    """
    Open a fresh database session and process one batch.
    """

    db = SessionLocal()

    try:
        return process_queue_batch(
            db=db,
            limit=QUEUE_BATCH_SIZE,
        )

    finally:
        db.close()


async def run_queue_worker(stop_event: asyncio.Event):
    """
    Continuously process eligible queue items until shutdown.
    """

    logger.info("Automatic packet queue worker started.")

    while not stop_event.is_set():

        try:

            result = await asyncio.to_thread(
                process_due_packets
            )

            if result.checked > 0:

                logger.info(
                    "Queue batch completed: checked=%s, synced=%s, "
                    "retry_scheduled=%s, failed=%s, expired=%s",
                    result.checked,
                    result.synced,
                    result.retry_scheduled,
                    result.failed,
                    result.expired,
                )

        except Exception:

            logger.exception(
                "Automatic packet queue processing failed. "
                "The worker will retry on its next cycle."
            )

        # Wait for the next polling cycle or an early shutdown signal.
        try:

            await asyncio.wait_for(
                stop_event.wait(),
                timeout=QUEUE_POLL_INTERVAL_SECONDS,
            )

        except asyncio.TimeoutError:
            pass

    logger.info("Automatic packet queue worker stopped.")
