import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# Import bot handlers
from app.bot_handlers import router
from app.middlewares import RateLimitMiddleware

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Initialize Bot and Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Register Rate Limiting Middleware
dp.message.middleware(RateLimitMiddleware(limit=10, window=60))

# Register the router from bot_handlers
dp.include_router(router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Server Started")
    # Start polling in the background
    polling_task = asyncio.create_task(dp.start_polling(bot))
    
    yield  # App runs here
    
    # Shutdown actions
    logger.info("Server Shutting Down")
    polling_task.cancel()
    await bot.session.close()

# Initialize FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Welcome to World Cup 2026 AI Bot API"}

@app.get("/health")
async def health_check():
    return {"status": "Bot and Server are running"}
