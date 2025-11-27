from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from typing import Dict, Any
from datetime import datetime

# Load environment variables from .env file
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="News API", version="1.0.0")

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client with environment variables
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY"),
)


def standard_response(
    success: bool = True, data: Dict[str, Any] = None, message: str = "Success"
):
    return {
        "success": success,
        "data": data,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/")
async def root():
    return {"message": "News API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/v1/articles")
async def get_articles(page: int = 1, limit: int = 10):
    try:
        offset = (page - 1) * limit
        response = (
            supabase.table("articles")
            .select("*")
            .eq("status", "published")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return standard_response(
            success=True,
            data={
                "articles": response.data,
                "page": page,
                "limit": limit,
                "total": len(response.data),
            },
            message="Articles retrieved",
        )
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PROCESSING_ERROR", "message": str(e)},
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/api/v1/articles/{article_id}")
async def get_article(article_id: str):
    try:
        response = (
            supabase.table("articles")
            .select("*")
            .eq("id", article_id)
            .single()
            .execute()
        )

        if not response.data:
            return {
                "success": False,
                "error": {"code": "NOT_FOUND", "message": "Article not found"},
                "timestamp": datetime.now().isoformat(),
            }

        # Update view count
        view_count = response.data.get("view_count", 0)
        supabase.table("articles").update({"view_count": view_count + 1}).eq(
            "id", article_id
        ).execute()

        return standard_response(
            success=True, data={"article": response.data}, message="Article retrieved"
        )
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PROCESSING_ERROR", "message": str(e)},
            "timestamp": datetime.now().isoformat(),
        }


@app.post("/api/v1/articles")
async def create_article(article_data: dict):
    try:
        response = (
            supabase.table("articles")
            .insert(
                {
                    "title": article_data.get("title"),
                    "summary": article_data.get("summary"),
                    "content": article_data.get("content"),
                    "category_id": article_data.get("category_id"),
                    "channel_id": article_data.get("channel_id"),
                    "author_id": article_data.get("author_id"),
                    "status": "published",
                    "view_count": 0,
                }
            )
            .execute()
        )

        return standard_response(
            success=True,
            data={"article": response.data[0] if response.data else None},
            message="Article created",
        )
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PROCESSING_ERROR", "message": str(e)},
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/api/v1/categories")
async def get_categories():
    try:
        response = supabase.table("categories").select("*").execute()

        return standard_response(
            success=True,
            data={"categories": response.data, "total": len(response.data)},
            message="Categories retrieved",
        )
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PROCESSING_ERROR", "message": str(e)},
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/api/v1/channels")
async def get_channels():
    try:
        response = supabase.table("channels").select("*").execute()

        return standard_response(
            success=True,
            data={"channels": response.data, "total": len(response.data)},
            message="Channels retrieved",
        )
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PROCESSING_ERROR", "message": str(e)},
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/api/v1/articles/{article_id}/comments")
async def get_comments(article_id: str):
    try:
        response = (
            supabase.table("comments")
            .select("*")
            .eq("article_id", article_id)
            .order("created_at", desc=True)
            .execute()
        )

        return standard_response(
            success=True,
            data={"comments": response.data, "total": len(response.data)},
            message="Comments retrieved",
        )
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PROCESSING_ERROR", "message": str(e)},
            "timestamp": datetime.now().isoformat(),
        }


@app.post("/api/v1/articles/{article_id}/comments")
async def add_comment(article_id: str, comment_data: dict):
    try:
        response = (
            supabase.table("comments")
            .insert(
                {
                    "article_id": article_id,
                    "user_id": comment_data.get("user_id"),
                    "body": comment_data.get("content"),
                }
            )
            .execute()
        )

        return standard_response(
            success=True,
            data={"comment": response.data[0] if response.data else None},
            message="Comment added",
        )
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PROCESSING_ERROR", "message": str(e)},
            "timestamp": datetime.now().isoformat(),
        }


@app.post("/api/v1/articles/{article_id}/bookmark")
async def bookmark_article(article_id: str, bookmark_data: dict):
    try:
        response = (
            supabase.table("bookmarks")
            .insert({"article_id": article_id, "user_id": bookmark_data.get("user_id")})
            .execute()
        )

        return standard_response(success=True, message="Article bookmarked")
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PROCESSING_ERROR", "message": str(e)},
            "timestamp": datetime.now().isoformat(),
        }


@app.delete("/api/v1/articles/{article_id}/bookmark")
async def remove_bookmark(article_id: str, bookmark_data: dict):
    try:
        supabase.table("bookmarks").delete().eq("article_id", article_id).eq(
            "user_id", bookmark_data.get("user_id")
        ).execute()

        return standard_response(success=True, message="Bookmark removed")
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PROCESSING_ERROR", "message": str(e)},
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/api/v1/users/me/bookmarks")
async def get_user_bookmarks(bookmark_data: dict):
    try:
        response = (
            supabase.table("bookmarks")
            .select("*")
            .eq("user_id", bookmark_data.get("user_id"))
            .execute()
        )

        return standard_response(
            success=True,
            data={"bookmarks": response.data, "total": len(response.data)},
            message="Bookmarks retrieved",
        )
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PROCESSING_ERROR", "message": str(e)},
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
