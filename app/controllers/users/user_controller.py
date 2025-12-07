from fastapi import APIRouter, HTTPException, Depends
from ...models.schemas import StandardResponse
from ...services.article_service import ArticleService
from ...services.user_service import UserService
from ...middleware.auth import get_current_user, require_admin

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


@router.get("/admin/all-profiles")
async def get_all_user_profiles(role: str = None, current_user = Depends(require_admin)):
    try:
        profiles = UserService.get_all_user_profiles(role_filter=role)
        return StandardResponse(
            success=True,
            data={"profiles": profiles},
            message="User profiles retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/admin/ban/{user_id}")
async def ban_user(user_id: str, current_user = Depends(require_admin)):
    try:
        UserService.ban_user(user_id)
        return StandardResponse(success=True, message="User banned")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/admin/unban/{user_id}")
async def unban_user(user_id: str, current_user = Depends(require_admin)):
    try:
        UserService.unban_user(user_id)
        return StandardResponse(success=True, message="User unbanned")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/admin/set-role/{user_id}")
async def set_user_role(user_id: str, role: str, current_user = Depends(require_admin)):
    try:
        if role not in ['admin', 'author', 'reader']:
            raise HTTPException(status_code=400, detail="Invalid role")

        UserService.update_user_role(user_id, role)
        return StandardResponse(success=True, message=f"User role updated to {role}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))