import asyncio
import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from app.database import get_redis_client

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 10, window: int = 60):
        """
        :param limit: Maximum number of messages allowed within the window.
        :param window: Time window in seconds.
        """
        self.limit = limit
        self.window = window
        self.redis = get_redis_client()
        # Fallback to in-memory dict if Redis is down
        self.local_cache = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        
        if self.redis:
            # Redis rate limiting logic
            key = f"rate_limit:{user_id}"
            current = await asyncio.to_thread(self.redis.get, key)
            
            if current and int(current) >= self.limit:
                await event.answer("⏳ Bạn gửi lệnh quá nhanh. Vui lòng chờ 1 phút trước khi thử lại!")
                return
            
            def update_redis():
                pipe = self.redis.pipeline()
                pipe.incr(key)
                if not current:
                    pipe.expire(key, self.window)
                pipe.execute()
                
            await asyncio.to_thread(update_redis)
        else:
            # Fallback local memory dictionary
            now = time.time()
            if user_id not in self.local_cache:
                self.local_cache[user_id] = []
            
            # Clean old records
            self.local_cache[user_id] = [t for t in self.local_cache[user_id] if now - t < self.window]
            
            if len(self.local_cache[user_id]) >= self.limit:
                await event.answer("⏳ Bạn gửi lệnh quá nhanh. Vui lòng chờ 1 phút trước khi thử lại!")
                return
                
            self.local_cache[user_id].append(now)

        return await handler(event, data)
