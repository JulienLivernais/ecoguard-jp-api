from app.core.config import settings
from fastapi import Request, HTTPException
import redis


redis_client = redis.from_url(settings.REDIS_URL)

def check_rate_limit(request: Request):
    ip = request.client.host
    key = f"bulletin_limit:{ip}"

    count = redis_client.get(key)

    if count and int(count) >= 3:
        raise HTTPException(
            status_code=429,
            detail="Daily bulletin limit reached (3 per day)."
        )

    pipeline = redis_client.pipeline()
    pipeline.incr(key)
    pipeline.expire(key, 86400)  # 24 hours in seconds
    pipeline.execute()







