from fastapi import APIRouter, HTTPException, Depends
from ...models.schemas import UserRegister, UserLogin, UserProfile, AuthorInvite, StandardResponse
from ...services.auth_service import AuthService
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
                profile_result = supabase.table("profiles").select("role_id, display_name").eq("user_id", auth_response.user.id).execute()
                if profile_result.data and len(profile_result.data) > 0:
                    profile = profile_result.data[0]
                    # Get role name from roles table
                    role_result = supabase.table("roles").select("name").eq("id", profile["role_id"]).execute()
                    if role_result.data and len(role_result.data) > 0:
                        user_role = role_result.data[0]["name"]
                    else:
                        user_role = "reader"
                    display_name = profile.get("display_name")
                else:
                    user_role = "reader"
                    display_name = None
            except Exception:
                user_role = "reader"
                display_name = None

            return StandardResponse(
                success=True,
                data={
                    "access_token": auth_response.session.access_token,
                    "user": {
                        "id": auth_response.user.id,
                        "email": auth_response.user.email,
                        "role": user_role,
                        "display_name": display_name
                    }
                },
                message="Login successful"
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    try:
        AuthService.logout()
        return StandardResponse(success=True, message="Logout successful")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    return StandardResponse(
        success=True,
        data={"user": current_user},
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

@router.post("/admin/invite-author")
async def invite_author(invite_data: AuthorInvite, current_user = Depends(require_admin)):
    try:
        # Use Supabase's built-in invitation system with admin client
        auth_response = supabase_admin.auth.admin.inviteUserByEmail(
            email=invite_data.email,
            data={
                "display_name": invite_data.display_name,
                "channel_id": invite_data.channel_id,
                "role": "author"
            }
        )

        if auth_response.user:
            return StandardResponse(
                success=True,
                data={
                    "user_id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "message": "Invitation sent successfully"
                },
                message="Author invitation sent successfully"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to send invitation")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/admin/set-role")
async def set_user_role(user_id: str, role: str, current_user = Depends(require_admin)):
    try:
        if role not in ['admin', 'author', 'reader']:
            raise HTTPException(status_code=400, detail="Invalid role")

        # Update user's role in auth.users table
        user_metadata = {"role": role}

        response = supabase_admin.auth.admin.updateUserById(
            user_id=user_id,
            attributes={"user_metadata": user_metadata}
        )

        if response.user:
            return StandardResponse(
                success=True,
                data={"user_id": user_id, "role": role},
                message=f"User role updated to {role}"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to update user role")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))