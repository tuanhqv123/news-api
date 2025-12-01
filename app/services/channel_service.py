from ..config.database import supabase
from typing import List, Dict, Any

class ChannelService:
    @staticmethod
    def create_channel(name: str, slug: str, description: str = None, rss_url: str = None, logo_url: str = None) -> Dict[str, Any]:
        """Create a new channel (admin only)"""
        try:
            channel_data = {
                "name": name,
                "slug": slug,
                "description": description,
                "rss_url": rss_url,
                "logo_url": logo_url,
                "is_active": True
            }

            response = supabase.table("channels").insert(channel_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise e

    @staticmethod
    def get_all_channels() -> List[Dict[str, Any]]:
        """Get all channels (admin only)"""
        try:
            response = supabase.table("channels").select("*").order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def get_active_channels() -> List[Dict[str, Any]]:
        """Get all active channels (public)"""
        try:
            response = supabase.table("channels").select("*").eq("is_active", True).order("name").execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def update_channel(
        channel_id: int,
        name: str = None,
        description: str = None,
        rss_url: str = None,
        logo_url: str = None,
        is_active: bool = None
    ) -> Dict[str, Any]:
        """Update a channel (admin only)"""
        try:
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            if rss_url is not None:
                update_data["rss_url"] = rss_url
            if logo_url is not None:
                update_data["logo_url"] = logo_url
            if is_active is not None:
                update_data["is_active"] = is_active

            response = supabase.table("channels").update(update_data).eq("id", channel_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise e

    @staticmethod
    def delete_channel(channel_id: int):
        """Delete a channel (admin only)"""
        try:
            # Check if channel has articles
            articles_count = supabase.table("articles").select("id", count="exact").eq("channel_id", channel_id).execute()
            if articles_count.count > 0:
                raise Exception("Cannot delete channel with existing articles")

            supabase.table("channels").delete().eq("id", channel_id).execute()
        except Exception as e:
            raise e

    @staticmethod
    def get_channel_by_id(channel_id: int) -> Dict[str, Any]:
        """Get a specific channel by ID"""
        try:
            response = supabase.table("channels").select("*").eq("id", channel_id).single().execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def follow_channel(channel_id: int, user_id: str) -> bool:
        """Follow a channel (reader only)"""
        try:
            # Check if already following
            existing = supabase.table("channel_followers").select("channel_id, user_id").eq("channel_id", channel_id).eq("user_id", user_id).execute()
            if existing.data:
                raise Exception("Already following this channel")

            # Add follow relationship
            supabase.table("channel_followers").insert({
                "channel_id": channel_id,
                "user_id": user_id
            }).execute()
            return True
        except Exception as e:
            raise e

    @staticmethod
    def unfollow_channel(channel_id: int, user_id: str) -> bool:
        """Unfollow a channel (reader only)"""
        try:
            # Remove follow relationship
            supabase.table("channel_followers").delete().eq("channel_id", channel_id).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            raise e

    @staticmethod
    def is_following_channel(channel_id: int, user_id: str) -> bool:
        """Check if user is following a channel"""
        try:
            response = supabase.table("channel_followers").select("channel_id").eq("channel_id", channel_id).eq("user_id", user_id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise e

    @staticmethod
    def get_followed_channels(user_id: str) -> List[Dict[str, Any]]:
        """Get all channels followed by a user"""
        try:
            response = supabase.table("channel_followers")\
                .select("channels(*)")\
                .eq("user_id", user_id)\
                .eq("channels.is_active", True)\
                .order("followed_at", desc=True)\
                .execute()

            # Extract channel data from the nested response
            followed_channels = []
            for item in response.data:
                if "channels" in item and item["channels"]:
                    # Include the followed_at timestamp in the channel data
                    channel_data = item["channels"]
                    channel_data["followed_at"] = item.get("followed_at")
                    followed_channels.append(channel_data)

            return followed_channels
        except Exception as e:
            raise e