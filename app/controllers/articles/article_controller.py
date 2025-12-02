from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ...models.schemas import ArticleCreate, CommentCreate, StandardResponse
from ...services.article_service import ArticleService
from ...middleware.auth import require_admin, require_author, require_reader
from ...config.database import supabase

router = APIRouter(prefix="/api/v1/articles", tags=["articles"])

@router.get("/")
async def get_articles(page: int = 1, limit: int = 10, category: Optional[int] = None):
    """Public endpoint to get published articles"""
    try:
        articles = ArticleService.get_articles(page, limit, category)
        return StandardResponse(
            success=True,
            data={"articles": articles, "page": page, "limit": limit},
            message="Articles retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_articles(q: str, page: int = 1, limit: int = 10):
    """Public endpoint to search published articles"""
    try:
        articles = ArticleService.search_articles(q, page, limit)
        return StandardResponse(
            success=True,
            data={"articles": articles, "page": page, "limit": limit},
            message="Articles searched"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{article_id}")
async def get_article(article_id: str):
    """Public endpoint to get a specific published article"""
    try:
        article = ArticleService.get_article(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return StandardResponse(
            success=True,
            data={"article": article},
            message="Article retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/")
async def create_article(article_data: ArticleCreate, current_user = Depends(require_author)):
    try:
        # For authors, check if they have a channel assigned and if the article channel matches
        if current_user.role == 'author':
            # Get user's profile to check channel_id
            profile_response = supabase.table("profiles").select("channel_id").eq("user_id", current_user.id).single().execute()

            if not profile_response.data or not profile_response.data.get('channel_id'):
                # Assign default channel (VnExpress) for testing
                article_data.channel_id = 1
            else:
                # Set channel_id to author's assigned channel
                article_data.channel_id = profile_response.data['channel_id']

        # For authors, articles should be created with default 'pending_review' status
        # For admins, they can set their own status
        article_data_dict = article_data.dict()
        if current_user.role == 'author':
            # Remove status from dict so it uses database default 'pending_review'
            article_data_dict.pop('status', None)

        article = ArticleService.create_article(article_data_dict, current_user.id)
        return StandardResponse(
            success=True,
            data={"article": article},
            message="Article created and pending approval" if current_user.role == 'author' else "Article created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{article_id}/comments")
async def get_comments(article_id: str):
    try:
        comments = ArticleService.get_comments(article_id)
        return StandardResponse(
            success=True,
            data={"comments": comments},
            message="Comments retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{article_id}/comments")
async def add_comment(article_id: str, comment_data: CommentCreate, current_user = Depends(require_reader)):
    try:
        comment = ArticleService.add_comment(article_id, comment_data, current_user.id)
        return StandardResponse(
            success=True,
            data={"comment": comment},
            message="Comment added"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{article_id}/bookmark")
async def bookmark_article(article_id: str, current_user = Depends(require_reader)):
    try:
        ArticleService.bookmark_article(article_id, current_user.id)
        return StandardResponse(success=True, message="Article bookmarked")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{article_id}/bookmark")
async def remove_bookmark(article_id: str, current_user = Depends(require_reader)):
    try:
        ArticleService.remove_bookmark(article_id, current_user.id)
        return StandardResponse(success=True, message="Bookmark removed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{article_id}/publish")
async def publish_article(article_id: str, current_user = Depends(require_admin)):
    try:
        ArticleService.publish_article(article_id)
        return StandardResponse(success=True, message="Article published")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/admin/all")
async def get_all_articles_admin(page: int = 1, limit: int = 10, current_user = Depends(require_admin)):
    try:
        articles = ArticleService.get_all_articles(page, limit)
        return StandardResponse(
            success=True,
            data={"articles": articles, "page": page, "limit": limit},
            message="All articles retrieved (admin)"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{article_id}/status")
async def update_article_status(article_id: str, status: str, current_user = Depends(require_admin)):
    try:
        ArticleService.update_article_status(article_id, status)
        return StandardResponse(success=True, message=f"Article status updated to {status}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/admin/pending")
async def get_pending_articles(current_user = Depends(require_admin)):
    try:
        articles = ArticleService.get_pending_articles()
        return StandardResponse(
            success=True,
            data={"articles": articles},
            message="Pending articles retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/admin/approve/{article_id}")
async def approve_article(article_id: str, current_user = Depends(require_admin)):
    try:
        article = ArticleService.approve_article(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        return StandardResponse(
            success=True,
            data={"article": article},
            message="Article approved and published"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/admin/reject/{article_id}")
async def reject_article(article_id: str, current_user = Depends(require_admin)):
    try:
        article = ArticleService.reject_article(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        return StandardResponse(
            success=True,
            data={"article": article},
            message="Article rejected"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))