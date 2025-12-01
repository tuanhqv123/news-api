from fastapi import APIRouter, HTTPException, Depends
from ...models.schemas import StandardResponse
from ...services.channel_service import ChannelService
from ...middleware.auth import get_current_user
from pydantic import BaseModel

class ChannelCreate(BaseModel):
    name: str
    slug: str
    description: str = None
    rss_url: str = None
    logo_url: str = None

router = APIRouter(prefix="/api/v1/channels", tags=["channels"])

@router.post("/admin/create")
async def create_channel(
    channel_data: ChannelCreate,
    current_user = Depends(get_current_user)
):
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin role required")
        
        channel = ChannelService.create_channel(
            name=channel_data.name,
            slug=channel_data.slug,
            description=channel_data.description,
            rss_url=channel_data.rss_url,
            logo_url=channel_data.logo_url
        )

        return StandardResponse(
            success=True,
            data={"channel": channel},
            message="Channel created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))@router.get("/admin/list")
async def list_channels(current_user = Depends(get_current_user)):
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin role required")

        channels = ChannelService.get_all_channels()
        return StandardResponse(
            success=True,
            data={"channels": channels},
            message="Channels retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/admin/{channel_id}")
async def update_channel(
    channel_id: int,
    name: str = None,
    description: str = None,
    rss_url: str = None,
    logo_url: str = None,
    is_active: bool = None,
    current_user = Depends(get_current_user)
):
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin role required")

        channel = ChannelService.update_channel(
            channel_id=channel_id,
            name=name,
            description=description,
            rss_url=rss_url,
            logo_url=logo_url,
            is_active=is_active
        )

        return StandardResponse(
            success=True,
            data={"channel": channel},
            message="Channel updated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/admin/{channel_id}")
async def delete_channel(channel_id: int, current_user = Depends(get_current_user)):
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin role required")

        ChannelService.delete_channel(channel_id)
        return StandardResponse(
            success=True,
            message="Channel deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/public/list")
async def get_public_channels():
    try:
        channels = ChannelService.get_active_channels()
        return StandardResponse(
            success=True,
            data={"channels": channels},
            message="Active channels retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def get_all_channels(current_user = Depends(get_current_user)):
    try:
        channels = ChannelService.get_all_channels()
        return StandardResponse(
            success=True,
            data={"channels": channels},
            message="All channels retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{channel_id}/follow")
async def follow_channel(channel_id: int, current_user = Depends(get_current_user)):
    try:
        if current_user.role != 'reader':
            raise HTTPException(status_code=403, detail="Reader role required")
        
        ChannelService.follow_channel(channel_id, current_user.id)
        return StandardResponse(
            success=True,
            message="Channel followed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{channel_id}/follow")
async def unfollow_channel(channel_id: int, current_user = Depends(get_current_user)):
    try:
        if current_user.role != 'reader':
            raise HTTPException(status_code=403, detail="Reader role required")

        ChannelService.unfollow_channel(channel_id, current_user.id)
        return StandardResponse(
            success=True,
            message="Channel unfollowed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/followed")
async def get_followed_channels(current_user = Depends(get_current_user)):
    try:
        if current_user.role != 'reader':
            raise HTTPException(status_code=403, detail="Reader role required")

        channels = ChannelService.get_followed_channels(current_user.id)
        return StandardResponse(
            success=True,
            data={"channels": channels},
            message="Followed channels retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))