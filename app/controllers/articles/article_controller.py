from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ...models.schemas import ArticleCreate, CommentCreate, StandardResponse
from ...services.article_service import ArticleService
from ...services.notification_service import notification_service
from ...middleware.auth import require_admin, require_author, require_reader
from ...config.database import supabase


router = APIRouter(prefix="/api/v1/articles", tags=["articles"])


@router.get("/")
async def get_articles(
    page: int = 1, 
    limit: int = 10, 
    category: Optional[int] = None,
    channel_id: Optional[int] = None  # ✅ THÊM
):
    """Public endpoint to get published articles"""
    try:
        articles = ArticleService.get_articles(page, limit, category, channel_id)  # ✅ THÊM
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


@router.get("/my-articles")
async def get_my_articles(page: int = 1, limit: int = 10, current_user = Depends(require_author)):
    """Get all articles created by the current user"""
    try:
        articles = ArticleService.get_user_articles(current_user.id, page, limit)
        return StandardResponse(
            success=True,
            data={"articles": articles, "page": page, "limit": limit},
            message="Your articles retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/all")
async def get_all_articles_admin(page: int = 1, limit: int = 10, current_user = Depends(require_admin)):
    """Admin endpoint to get all articles regardless of status"""
    try:
        articles = ArticleService.get_all_articles(page, limit)
        return StandardResponse(
            success=True,
            data={"articles": articles, "page": page, "limit": limit},
            message="All articles retrieved (admin)"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/pending")
async def get_pending_articles(current_user = Depends(require_admin)):
    """Admin endpoint to get pending articles"""
    try:
        articles = ArticleService.get_pending_articles()
        return StandardResponse(
            success=True,
            data={"articles": articles},
            message="Pending articles retrieved"
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


@router.get("/{article_id}/share-link")
async def get_share_link(article_id: str):
    """Generate shareable deep link for article"""
    try:
        article = ArticleService.get_article(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        deep_link = f"newsapp://article/{article_id}"
        web_fallback = f"http://10.0.2.2:8000/article/{article_id}"
        
        return StandardResponse(
            success=True,
            data={
                "deep_link": deep_link,
                "web_fallback": web_fallback,
                "title": article["title"],
                "description": article.get("summary", "")
            },
            message="Share link generated"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_article(article_data: ArticleCreate, current_user = Depends(require_author)):
    """Create new article"""
    try:
        if current_user.role == 'author':
            profile_response = supabase.table("profiles").select("channel_id").eq("user_id", current_user.id).single().execute()

            if not profile_response.data or not profile_response.data.get('channel_id'):
                article_data.channel_id = 1
            else:
                article_data.channel_id = profile_response.data['channel_id']

        article_data_dict = article_data.dict()
        if current_user.role == 'author':
            article_data_dict.pop('status', None)

        article = ArticleService.create_article(article_data_dict, current_user.id)

        if current_user.role == 'author':
            author_name = current_user.display_name or current_user.email
            try:
                notification_service.notify_admins_new_article(
                    article_title=article["title"],
                    author_name=author_name,
                    article_id=article["id"]
                )
            except Exception:
                pass

        return StandardResponse(
            success=True,
            data={"article": article},
            message="Article created and pending approval" if current_user.role == 'author' else "Article created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{article_id}/comments")
async def get_comments(article_id: str):
    """Get comments for article"""
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
    """Add comment to article"""
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
    """Bookmark article"""
    try:
        ArticleService.bookmark_article(article_id, current_user.id)
        return StandardResponse(success=True, message="Article bookmarked")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{article_id}/bookmark")
async def remove_bookmark(article_id: str, current_user = Depends(require_reader)):
    """Remove bookmark"""
    try:
        ArticleService.remove_bookmark(article_id, current_user.id)
        return StandardResponse(success=True, message="Bookmark removed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{article_id}/status")
async def update_article_status(article_id: str, status: str, current_user = Depends(require_admin)):
    """Update article status (admin only)"""
    try:
        article_response = supabase.table("articles").select("*").eq("id", article_id).single().execute()
        if not article_response.data:
            raise HTTPException(status_code=404, detail="Article not found")

        article = article_response.data
        updated_article = ArticleService.update_article_status(article_id, status)

        if article.get("user_id") and article.get("status") != status:
            try:
                author_response = supabase.table("profiles").select("display_name").eq("user_id", article["user_id"]).single().execute()
                author_name = author_response.data.get("display_name", "Unknown Author") if author_response.data else "Unknown Author"

                notification_service.notify_author_status_change(
                    article_title=article["title"],
                    status=status,
                    author_user_id=article["user_id"],
                    article_id=article_id
                )

                notification_service.notify_admins_status_change(
                    article_title=article["title"],
                    status=status,
                    author_name=author_name,
                    article_id=article_id
                )

            except Exception:
                pass

        return StandardResponse(
            success=True,
            data={"article": updated_article},
            message=f"Article status updated to {status}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
