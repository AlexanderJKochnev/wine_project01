# app/core/utils/loggers.py
from asyncio import sleep
from random import uniform
from app.core.config.project_config import settings


async def smooth_delay():
    # smooth pasing delay
    min_delay = settings.ARQ_MIN_DELAY
    max_delay = settings.ARQ_MAX_DELAY
    delay = uniform(min_delay, max_delay)
    await sleep(delay)
