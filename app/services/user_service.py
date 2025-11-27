from ..config.database import supabase

class UserService:
    @staticmethod
    def get_pending_authors():
        try:
            # This would need a table to track author requests
            # For now, return users with 'pending_author' role or similar
            response = supabase.table("auth.users").select("*").execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def approve_author(user_id: str):
        try:
            # Update user role to 'author' using secure RPC function
            response = supabase.rpc('update_user_role', {
                'target_user_id': user_id,
                'new_role': 'author'
            }).execute()
            return {"message": "Author approved successfully"}
        except Exception as e:
            raise e

    @staticmethod
    def update_user_role(user_id: str, role: str):
        try:
            # Update user role using secure RPC function
            response = supabase.rpc('update_user_role', {
                'target_user_id': user_id,
                'new_role': role
            }).execute()
            return {"message": f"User role updated to {role}"}
        except Exception as e:
            raise e

    @staticmethod
    def get_all_user_profiles():
        try:
            # Get profiles with user info from auth.users
            response = supabase.table("profiles").select(
                "*, auth.users!inner(email, created_at, banned_until)"
            ).execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def ban_user(user_id: str):
        try:
            # Ban user by setting banned_until to a future date (e.g., 100 years from now)
            from datetime import datetime, timedelta
            banned_until = datetime.now() + timedelta(days=36500)  # 100 years
            response = supabase.rpc('ban_user', {
                'target_user_id': user_id,
                'ban_until': banned_until.isoformat()
            }).execute()
            return {"message": "User banned successfully"}
        except Exception as e:
            raise e

    @staticmethod
    def unban_user(user_id: str):
        try:
            # Unban user by setting banned_until to null
            response = supabase.rpc('ban_user', {
                'target_user_id': user_id,
                'ban_until': None
            }).execute()
            return {"message": "User unbanned successfully"}
        except Exception as e:
            raise e

    @staticmethod
    def invite_author(email: str, channel_id: int):
        try:
            # For testing: Just return success and note that we need to manually create the user
            # In production, this would use Supabase admin API
            return {
                "message": f"Invitation would be sent to {email} for channel {channel_id}",
                "email": email,
                "channel_id": channel_id,
                "role": "author"
            }
        except Exception as e:
            raise e