from ..config.database import supabase
from ..models.schemas import UserRegister, UserLogin

class AuthService:
    @staticmethod
    def register(user_data: UserRegister):
        try:
            auth_response = supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "display_name": user_data.display_name or user_data.email.split("@")[0]
                    }
                }
            })
            
            # If user was created, create profile
            if auth_response.user:
                # Create profile with default values
                profile_data = {
                    "user_id": auth_response.user.id,
                    "display_name": auth_response.user.user_metadata.get("display_name")
                }
                
                # Check if user has invitation data in metadata for channel_id
                if hasattr(auth_response.user, 'user_metadata') and auth_response.user.user_metadata:
                    invited_channel_id = auth_response.user.user_metadata.get('channel_id')
                    if invited_channel_id:
                        profile_data["channel_id"] = invited_channel_id
                
                # Create the profile
                supabase.table("profiles").insert(profile_data).execute()
            
            return auth_response
        except Exception as e:
            raise e

    @staticmethod
    def login(user_data: UserLogin):
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password
            })
            return auth_response
        except Exception as e:
            raise e

    @staticmethod
    def logout():
        try:
            supabase.auth.sign_out()
            return True
        except Exception as e:
            raise e

    @staticmethod
    def get_current_user(token: str):
        try:
            user = supabase.auth.get_user(token)
            return user.user if user.user else None
        except Exception as e:
            raise e

    @staticmethod
    def update_profile(profile_data: dict):
        try:
            return supabase.auth.update_user({"data": profile_data})
        except Exception as e:
            raise e