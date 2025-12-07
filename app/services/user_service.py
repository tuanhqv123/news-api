from ..config.database import supabase, supabase_admin

class UserService:
    @staticmethod
    def get_pending_authors():
        try:
            # Get users who have articles with 'pending_review' status
            # or users with author role that need approval
            response = supabase.rpc('get_pending_authors').execute()

            # Fallback: Use direct query if RPC doesn't exist
            if hasattr(response, 'error') and response.error:
                # Query users with pending articles or author role
                pending_response = supabase.table("profiles").select(
                    """
                    user_id,
                    display_name,
                    avatar_url,
                    roles(name, description)
                    """
                ).execute()

                pending_users = []
                for profile in pending_response.data or []:
                    # Get user auth info
                    try:
                        user_response = supabase_admin.auth.admin.get_user_by_id(profile['user_id'])
                        if user_response and user_response.user:
                            profile['email'] = user_response.user.email
                            profile['created_at'] = user_response.user.created_at
                    except:
                        profile['email'] = None
                        profile['created_at'] = None

                    # Check if user has pending articles
                    articles_response = supabase.table("articles").select("id", "title", "status", "created_at").eq("user_id", profile['user_id']).eq("status", "pending_review").execute()

                    if articles_response.data and len(articles_response.data) > 0:
                        profile['pending_articles'] = articles_response.data
                        profile['pending_reason'] = 'Has pending articles'
                        pending_users.append(profile)
                    elif profile.get('roles') and profile['roles'].get('name') == 'author':
                        profile['pending_articles'] = []
                        profile['pending_reason'] = 'Author role approval needed'
                        pending_users.append(profile)

                return pending_users

            return response.data

        except Exception as e:
            raise e

    @staticmethod
    def approve_author(user_id: str):
        try:
            # Get author role ID from roles table
            roles_response = supabase.table("roles").select("id").eq("name", "author").execute()
            if not roles_response.data:
                raise Exception("Author role not found")

            author_role_id = roles_response.data[0]["id"]

            # Update user's profile to have author role
            response = supabase.table("profiles").update({"role_id": author_role_id}).eq("user_id", user_id).execute()

            if not response.data:
                raise Exception("User not found or update failed")

            return {"message": "Author approved successfully"}
        except Exception as e:
            raise e

    @staticmethod
    def update_user_role(user_id: str, role: str):
        try:
            # Get role ID from roles table
            roles_response = supabase.table("roles").select("id").eq("name", role).execute()
            if not roles_response.data:
                raise Exception(f"Role '{role}' not found")

            role_id = roles_response.data[0]["id"]

            # Update user's profile to have the new role
            response = supabase.table("profiles").update({"role_id": role_id}).eq("user_id", user_id).execute()

            if not response.data:
                raise Exception("User not found or update failed")

            return {"message": f"User role updated to {role}"}
        except Exception as e:
            raise e

    @staticmethod
    def get_all_user_profiles(role_filter=None):
        try:
            # Build query with optional role filter
            if role_filter:
                # First get role_id from roles table
                role_response = supabase.table("roles").select("id").eq("name", role_filter).execute()
                if not role_response.data:
                    return []
                role_id = role_response.data[0]["id"]

                # Filter by role_id
                response = supabase.table("profiles").select(
                    "*, roles(name, description)"
                ).eq("role_id", role_id).execute()
            else:
                # Get all profiles
                response = supabase.table("profiles").select(
                    "*, roles(name, description)"
                ).execute()

            profiles = response.data or []

            # Get user email and auth info using admin client
            for profile in profiles:
                try:
                    user_response = supabase_admin.auth.admin.get_user_by_id(profile['user_id'])
                    if user_response and hasattr(user_response, 'user') and user_response.user:
                        user = user_response.user
                        profile['email'] = user.email
                        profile['created_at'] = user.created_at
                        profile['banned_until'] = getattr(user, 'banned_until', None)
                        profile['is_super_admin'] = getattr(user, 'is_super_admin', False)
                    else:
                        profile['email'] = None
                        profile['created_at'] = None
                        profile['banned_until'] = None
                        profile['is_super_admin'] = False
                except Exception as e:
                    print(f"Error fetching user {profile['user_id']}: {str(e)}")
                    profile['email'] = None
                    profile['created_at'] = None
                    profile['banned_until'] = None
                    profile['is_super_admin'] = False

            return profiles
        except Exception as e:
            raise e

    @staticmethod
    def ban_user(user_id: str):
        try:
            # Ban user using Supabase's built-in ban_duration parameter
            supabase_admin.auth.admin.update_user_by_id(
                user_id,
                {'ban_duration': '876000h'}  # Ban for 100 years (100 * 365 * 24 hours)
            )

            return {"message": "User banned successfully"}
        except Exception as e:
            raise e

    @staticmethod
    def unban_user(user_id: str):
        try:
            # Unban user by setting ban_duration to '0s' (zero seconds)
            supabase_admin.auth.admin.update_user_by_id(
                user_id,
                {'ban_duration': '0s'}
            )

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