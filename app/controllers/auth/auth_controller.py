from fastapi import APIRouter, HTTPException, Depends
from ...models.schemas import UserRegister, UserLogin, UserProfile, AuthorInvite, UserInvite, UserResponse, StandardResponse, LogoutRequest
from ...services.auth_service import AuthService
from ...services.role_service import RoleService
from ...middleware.auth import get_current_user, require_admin, require_author, require_any_auth
from ...config.database import supabase_admin, supabase
import secrets

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register")
async def register(user_data: UserRegister):
    try:
        # Default role is reader for public registration
        user_metadata = {"role": "reader"}
        if user_data.display_name:
            user_metadata["display_name"] = user_data.display_name

        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": user_metadata
            }
        })

        if auth_response.user:
            # Create profile entry
            try:
                profile_data = {
                    "user_id": auth_response.user.id,
                    "display_name": user_data.display_name,
                    "created_at": "now()",
                    "updated_at": "now()"
                }
                supabase.table("profiles").insert(profile_data).execute()
            except Exception:
                # Profile might already exist, ignore
                pass

            return StandardResponse(
                success=True,
                data={
                    "user_id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "role": "reader",
                    "message": "Please check your email to confirm your account"
                },
                message="User registered successfully. Please check your email to confirm your account."
            )
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(user_data: UserLogin):
    try:
        auth_response = AuthService.login(user_data)
        if auth_response.session:
            # Check user's role from profiles table
            try:
                profile_result = supabase.table("profiles").select("role_id, display_name, avatar_url").eq("user_id", auth_response.user.id).execute()
                if profile_result.data and len(profile_result.data) > 0:
                    profile = profile_result.data[0]
                    # Get role name from roles table
                    role_result = supabase.table("roles").select("name").eq("id", profile["role_id"]).execute()
                    if role_result.data and len(role_result.data) > 0:
                        user_role = role_result.data[0]["name"]
                    else:
                        user_role = "reader"
                    display_name = profile.get("display_name")
                    avatar_url = profile.get("avatar_url")
                else:
                    user_role = "reader"
                    display_name = None
                    avatar_url = None
            except Exception:
                user_role = "reader"
                display_name = None
                avatar_url = None

            return StandardResponse(
                success=True,
                data={
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,  # Add refresh token
                    "user": {
                        "id": auth_response.user.id,
                        "email": auth_response.user.email,
                        "role": user_role,
                        "display_name": display_name,
                        "avatar_url": avatar_url
                    }
                },
                message="Login successful"
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
async def logout(
    logout_data: LogoutRequest,
    current_user = Depends(get_current_user)
):
    """
    Logout user and optionally set device token to guest mode
    """
    try:
        # Logout from Supabase auth
        AuthService.logout()

        # If fcm_token is provided, set user_id to null (guest mode)
        if logout_data.fcm_token:
            supabase.table("users_devices")\
                .update({"user_id": None})\
                .eq("fcm_token", logout_data.fcm_token)\
                .execute()

        return StandardResponse(
            success=True,
            message="Logout successful"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    user_response = UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        channel_id=current_user.channel_id
    )
    return StandardResponse(
        success=True,
        data={"user": user_response.model_dump()},
        message="User profile retrieved"
    )

@router.put("/me")
async def update_profile(profile_data: UserProfile, current_user = Depends(get_current_user)):
    try:
        update_data = {}
        if profile_data.display_name is not None:
            update_data["display_name"] = profile_data.display_name
        if profile_data.avatar_url is not None:
            update_data["avatar_url"] = profile_data.avatar_url

        if update_data:
            update_data["updated_at"] = "now()"
            supabase.table("profiles").update(update_data).eq("user_id", current_user.id).execute()

        return StandardResponse(success=True, message="Profile updated")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/admin/invite-user")
async def invite_user(invite_data: UserInvite, current_user = Depends(require_admin)):
    try:
        # Get role name from role_id
        role_result = supabase.table("roles").select("name").eq("id", invite_data.role_id).execute()
        if not role_result.data:
            raise HTTPException(status_code=400, detail="Invalid role_id")
        role_name = role_result.data[0]["name"]

        # Use Supabase's built-in invitation system with admin client
        user_metadata = {
            "role": role_name,
            "role_id": invite_data.role_id,
            "invited_by": invite_data.invited_by
        }
        if invite_data.channel_id:
            user_metadata["channel_id"] = invite_data.channel_id

        auth_response = supabase_admin.auth.admin.invite_user_by_email(
            email=invite_data.email,
            options={
                "data": user_metadata
            }
        )

        if auth_response.user:
            return StandardResponse(
                success=True,
                data={
                    "user_id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "role": role_name,
                    "message": "Invitation sent successfully"
                },
                message="User invitation sent successfully"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to send invitation")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    try:
        # Use Supabase to refresh the session
        auth_response = supabase.auth.refresh_session(refresh_token)
        if auth_response.session:
            return StandardResponse(
                success=True,
                data={
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token  # Include new refresh token
                },
                message="Token refreshed successfully"
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))