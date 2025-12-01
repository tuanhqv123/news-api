from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..config.database import supabase

security = HTTPBearer()

class CustomUser:
    def __init__(self, supabase_user, profile_data):
        self.id = supabase_user.id
        self.email = supabase_user.email
        self.role = profile_data.get('roles', {}).get('name')
        self.display_name = profile_data.get('display_name')
        self.avatar_url = profile_data.get('avatar_url')
        self.channel_id = profile_data.get('channel_id')

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        user = supabase.auth.get_user(token)
        if not user.user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get role and profile data from profiles table (joining with roles table)
        profile_response = supabase.table("profiles")\
                    .select("role_id, roles!inner(name), display_name, avatar_url, channel_id")\
                    .eq("user_id", user.user.id)\
                    .single()\
                    .execute()

        if not profile_response.data:
            raise HTTPException(status_code=403, detail="User profile not found. Access denied.")

        profile_data = profile_response.data
        custom_user = CustomUser(user.user, profile_data)

        return custom_user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

async def get_current_user_with_role(required_role: str):
    async def role_dependency(current_user = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Access forbidden. {required_role.title()} role required."
            )
        return current_user
    return role_dependency

async def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Access forbidden. Admin role required."
        )
    return current_user

async def require_author(current_user = Depends(get_current_user)):
    if current_user.role != 'author':
        raise HTTPException(
            status_code=403,
            detail="Access forbidden. Author role required."
        )
    return current_user

async def require_reader(current_user = Depends(get_current_user)):
    if current_user.role != 'reader':
        raise HTTPException(
            status_code=403,
            detail="Access forbidden. Reader role required."
        )
    return current_user

async def require_any_auth(current_user = Depends(get_current_user)):
    # Any authenticated user can access
    return current_user

async def require_author_or_reader(current_user = Depends(get_current_user)):
    if current_user.role not in ['author', 'reader']:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden. Author or Reader role required."
        )
    return current_user