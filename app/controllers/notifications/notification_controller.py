from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict
from ...models.schemas import DeviceTokenRegister, SendNotificationRequest, StandardResponse
from ...middleware.auth import get_current_user
from ...config.database import supabase

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

@router.post("/set-token")
async def set_device_token(token_data: DeviceTokenRegister):
    """
    Set/update a device token for push notifications (public endpoint)
    Handles both guest users (user_id=null) and logged-in users
    """
    try:
        # Check if token already exists
        existing_token = supabase.table("users_devices")\
            .select("*")\
            .eq("fcm_token", token_data.fcm_token)\
            .execute()

        if existing_token.data:
            # Update existing token with new user_id and timestamp
            # This handles: guest->login, login->logout, user->device change
            update_data = {
                "user_id": token_data.user_id,
                "last_used_at": "now()"
            }

            # Only update device_type if it's different
            if existing_token.data[0]["device_type"] != token_data.device_type:
                update_data["device_type"] = token_data.device_type

            supabase.table("users_devices")\
                .update(update_data)\
                .eq("fcm_token", token_data.fcm_token)\
                .execute()
        else:
            # Insert new token
            device_data = {
                "user_id": token_data.user_id,
                "fcm_token": token_data.fcm_token,
                "device_type": token_data.device_type,
                "created_at": "now()",
                "last_used_at": "now()"
            }
            supabase.table("users_devices").insert(device_data).execute()

        return StandardResponse(
            success=True,
            message="Device token set successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-devices")
async def get_my_devices(user_id: Optional[str] = None):
    """
    Get devices for a user (public endpoint)
    If user_id is provided, returns devices for that user
    If user_id is null or not provided, returns all guest devices
    """
    try:
        query = supabase.table("users_devices")\
            .select("fcm_token", "device_type", "last_used_at", "created_at")

        # Filter by user_id if provided
        if user_id is not None:
            query = query.eq("user_id", user_id)
        else:
            # If no user_id specified, only return guest devices
            query = query.is_("user_id", "null")

        result = query.execute()

        return StandardResponse(
            success=True,
            data={"devices": result.data},
            message="Devices retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/send")
async def send_notification(request: SendNotificationRequest):
    """
    Send push notifications to specific FCM tokens
    Reuses the existing send_notification method from NotificationService
    **No authentication required - public endpoint**
    """
    try:
        from ...services.notification_service import notification_service

        # Use the existing send_notification method
        result = notification_service.send_notification(
            title=request.title,
            body=request.body,
            fcm_tokens=request.fcm_tokens,
            data=request.data,
            image_url=request.image_url
        )

        return StandardResponse(
            success=result["success"],
            data=result,
            message="Notifications sent successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))