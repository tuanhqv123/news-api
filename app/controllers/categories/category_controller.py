from fastapi import APIRouter, HTTPException, Depends
from ...models.schemas import StandardResponse
from ...services.category_service import CategoryService
from ...services.channel_service import ChannelService
from ...services.article_service import ArticleService
from ...middleware.auth import require_admin, require_any_auth
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])

class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: str = None
    parent_id: int = None

class ChannelCreate(BaseModel):
    name: str
    slug: str
    description: str = None
    rss_url: str = None
    logo_url: str = None

@router.get("/")
async def get_categories():
    """Public endpoint to get all categories"""
    try:
        categories = CategoryService.get_categories()
        return StandardResponse(
            success=True,
            data={"categories": categories},
            message="Categories retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{category_id}")
async def get_category_articles(category_id: int, page: int = 1, limit: int = 10):
    """Public endpoint to get articles in a specific category"""
    try:
        articles = ArticleService.get_articles(page, limit, category_id)
        return StandardResponse(
            success=True,
            data={"articles": articles, "page": page, "limit": limit},
            message="Category articles retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/channels")
async def get_channels():
    """Public endpoint to get all active channels"""
    try:
        channels = ArticleService.get_channels()
        return StandardResponse(
            success=True,
            data={"channels": channels},
            message="Channels retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/channels/{channel_id}/subscribe")
async def subscribe_channel(channel_id: int, current_user = Depends(require_any_auth)):
    try:
        ArticleService.subscribe_channel(channel_id, current_user.id)
        return StandardResponse(success=True, message="Channel subscribed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/channels/{channel_id}/subscribe")
async def unsubscribe_channel(channel_id: int, current_user = Depends(require_any_auth)):
    try:
        ArticleService.unsubscribe_channel(channel_id, current_user.id)
        return StandardResponse(success=True, message="Channel unsubscribed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/admin/create")
async def create_category(category_data: CategoryCreate, current_user = Depends(require_admin)):
    try:
        category = CategoryService.create_category(
            category_data.dict(),
            current_user.id
        )
        return StandardResponse(
            success=True,
            data={"category": category},
            message="Category created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))