import asyncio
from generator import Generator
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Starting IoT data generator...")

async def run_with_timeout(generator, timeout_seconds):
    """Runs the generator for a specified timeout."""
    try:
        await asyncio.wait_for(generator.generate(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.info(f"Generator stopped after {timeout_seconds} seconds.")

if __name__ == "__main__":
    generator = Generator()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_with_timeout(generator, 300))
    loop.close()
