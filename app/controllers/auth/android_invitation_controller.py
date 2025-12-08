from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from app.config.database import supabase, supabase_admin

router = APIRouter(prefix="/api/v1/auth", tags=["android-auth"])

class VerifyInviteRequest(BaseModel):
    token_hash: str

class SetupPasswordRequest(BaseModel):
    password: str
    token_hash: str

@router.post("/verify-invite")
async def verify_invite(request: VerifyInviteRequest):
    """Verify invitation token for Android app"""
    try:
        # Verify the invitation token
        response = supabase.auth.verify_otp({
            'token_hash': request.token_hash,
            'type': 'invite'
        })

        if response.user is None:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid or expired invitation",
                    "error_code": "INVALID_INVITE"
                }
            )

        return {
            "success": True,
            "data": {
                "user_id": response.user.id,
                "email": response.user.email,
                "user_metadata": response.user.user_metadata or {}
            },
            "message": "Invitation verified successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Invalid or expired invitation",
                "error_code": "INVALID_INVITE"
            }
        )

@router.post("/setup-password")
async def setup_password(request: SetupPasswordRequest):
    """Set password for invited user (single step)"""
    print(f"=== SETUP PASSWORD REQUEST ===")
    print(f"Password length: {len(request.password)}")
    print(f"Token hash: {request.token_hash[:20]}...")
    print(f"================================")

    try:
        # Validate password
        if len(request.password) < 6:
            print("ERROR: Password too short")
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Password must be at least 6 characters long",
                    "error_code": "PASSWORD_TOO_SHORT"
                }
            )

        # First verify the token to get user info
        print("Verifying token and getting user info...")
        try:
            verify_response = supabase.auth.verify_otp({
                'token_hash': request.token_hash,
                'type': 'invite'
            })
        except Exception as e:
            print(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid or expired invitation",
                    "error_code": "INVALID_INVITE"
                }
            )

        if verify_response.user is None:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid invitation",
                    "error_code": "INVALID_INVITE"
                }
            )

        # Get user_id from verification
        user_id = verify_response.user.id
        print(f"User verified: {user_id}")

        # Update user password using admin method
        # Note: This requires service role key
        print("Attempting to update password...")
        print(f"Service role key exists: {bool(supabase_admin.supabase_key[:10] + '...')}")

        try:
            # Use the admin client for this
            update_response = supabase_admin.auth.admin.update_user_by_id(
                user_id,
                {'password': request.password}
            )
            print(f"Update response: {update_response}")
            print(f"Update response user: {update_response.user}")

            # Check if update was successful
            if update_response.user is None:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "success": False,
                        "error": "Failed to update password - no user returned",
                        "error_code": "PASSWORD_UPDATE_FAILED"
                    }
                )

        except HTTPException:
            raise
        except Exception as e:
            # Log the actual error for debugging
            print(f"ERROR updating password: {str(e)}")
            print(f"ERROR type: {type(e).__name__}")

            # Fallback for non-admin
            error_response = {
                "success": False,
                "error": "Failed to update password",
                "error_code": "PASSWORD_UPDATE_FAILED",
                "details": str(e)
            }
            raise HTTPException(status_code=500, detail=error_response)

        return {
            "success": True,
            "message": "Password set successfully. You can now login with your email and password."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR"
            }
        )

@router.get("/callback")
async def auth_callback(request: Request, token_hash: Optional[str] = None, type: Optional[str] = None):
    """Handle auth callback for deep linking"""
    if type == "invite" and token_hash:
        # Create deep link for Android app
        deep_link = f"newsapp://auth/invite?token_hash={token_hash}"

        # For mobile detection
        user_agent = request.headers.get("user-agent", "").lower()

        if "android" in user_agent or "iphone" in user_agent or "ipad" in user_agent:
            # Mobile device - return HTML page with JavaScript redirect
            html_content = f"""
            <html>
                <head>
                    <meta http-equiv="refresh" content="0; url={deep_link}">
                    <title>Opening News App...</title>
                </head>
                <body>
                    <h1>Opening News App...</h1>
                    <p>If the app doesn't open, <a href="{deep_link}">click here</a>.</p>
                </body>
            </html>
            """
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content=html_content)
        else:
            # Desktop - show instructions
            return {
                "message": "Please open this link on your mobile device to continue setup",
                "deep_link": deep_link,
                "user_agent": user_agent
            }

    # Handle invalid callback
    raise HTTPException(
        status_code=400,
        detail={
            "error": "Invalid callback parameters",
            "message": "Required: token_hash and type=invite"
        }
    )