from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings

app = FastAPI(
    title="News API",
    description="A news management API built with FastAPI and Supabase",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.controllers.auth.auth_controller import router as auth_router
from app.controllers.articles.article_controller import router as article_router
from app.controllers.users.user_controller import router as user_router
from app.controllers.categories.category_controller import router as category_router
from app.controllers.channels.channel_controller import router as channel_router

app.include_router(auth_router)
app.include_router(article_router)
app.include_router(user_router)
app.include_router(category_router)
app.include_router(channel_router)

@app.get("/")
async def root():
    return {"message": "News API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)