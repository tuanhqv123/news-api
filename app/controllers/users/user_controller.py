from fastapi import APIRouter, HTTPException, Depends
from ...models.schemas import StandardResponse
from ...services.article_service import ArticleService
from ...services.user_service import UserService
from ...middleware.auth import get_current_user
from pydantic import BaseModel

class InviteAuthorRequest(BaseModel):
    email: str
    channel_id: int

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/me/bookmarks")
async def get_user_bookmarks(current_user = Depends(get_current_user)):
    try:
        bookmarks = ArticleService.get_user_bookmarks(current_user.id)
        return StandardResponse(
            success=True,
            data={"bookmarks": bookmarks},
            message="Bookmarks retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/pending-authors")
async def get_pending_authors(current_user = Depends(get_current_user)):
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin role required")
        
        users = UserService.get_pending_authors()
        return StandardResponse(
            success=True,
            data={"users": users},
            message="Pending authors retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/admin/approve-author/{user_id}")
async def approve_author(user_id: str, current_user = Depends(get_current_user)):
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin role required")
        
        UserService.approve_author(user_id)
        return StandardResponse(success=True, message="Author approved")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/admin/all-profiles")
async def get_all_user_profiles(current_user = Depends(get_current_user)):
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin role required")
        
        profiles = UserService.get_all_user_profiles()
        return StandardResponse(
            success=True,
            data={"profiles": profiles},
            message="All user profiles retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/admin/ban/{user_id}")
async def ban_user(user_id: str, current_user = Depends(get_current_user)):
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin role required")
        
        UserService.ban_user(user_id)
        return StandardResponse(success=True, message="User banned")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/admin/unban/{user_id}")
async def unban_user(user_id: str, current_user = Depends(get_current_user)):
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin role required")
        
        UserService.unban_user(user_id)
        return StandardResponse(success=True, message="User unbanned")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/admin/invite-author")
async def invite_author(
    invite_data: InviteAuthorRequest,
    current_user = Depends(get_current_user)
):
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin role required")
        
        result = UserService.invite_author(invite_data.email, invite_data.channel_id)
        return StandardResponse(
            success=True,
            data={"invitation": result},
            message="Author invitation sent"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))