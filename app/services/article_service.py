from ..config.database import supabase
from ..models.schemas import ArticleCreate, CommentCreate

class ArticleService:
    @staticmethod
    def get_articles(page: int = 1, limit: int = 10, category: int = None):
        try:
            offset = (page - 1) * limit
            
            if category:
                # First get article_ids that belong to the category
                category_articles = supabase.table("article_categories").select("article_id").eq("category_id", category).execute()
                article_ids = [item["article_id"] for item in category_articles.data]
                
                if not article_ids:
                    return []
                
                # Then get articles with those IDs
                response = supabase.table("articles").select(
                    "*, article_categories(*), channels(*)"
                ).eq("status", "published").in_("id", article_ids).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            else:
                # Get all published articles
                response = supabase.table("articles").select(
                    "*, article_categories(*), channels(*)"
                ).eq("status", "published").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def get_article(article_id: str):
        try:
            response = supabase.table("articles").select(
                "*, article_categories(*), channels(*)"
            ).eq("id", article_id).single().execute()

            if response.data:
                supabase.table("articles").update({"view_count": (response.data["view_count"] or 0) + 1}).eq("id", article_id).execute()

            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def get_user_profile(user_id: str):
        try:
            response = supabase.table("profiles").select("*").eq("user_id", user_id).single().execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def create_article(article_data: dict, user_id: str):
        try:
            import re
            from datetime import datetime
            base_slug = re.sub(r'[^\w\s-]', '', article_data['title']).strip().lower()
            base_slug = re.sub(r'[-\s]+', '-', base_slug)
            slug = base_slug
            # Check if slug exists, if yes, append timestamp
            existing = supabase.table("articles").select("id").eq("slug", slug).execute()
            if existing.data:
                slug = f"{base_slug}-{int(datetime.now().timestamp())}"
            
            # Build the insert data
            insert_data = {
                "title": article_data['title'],
                "slug": slug,
                "summary": article_data['summary'],
                "content": article_data['content'],
                "channel_id": article_data['channel_id'],
                "user_id": user_id,  # Add the user who created the article
                "view_count": 0,
                "hero_image_url": article_data.get('hero_image_url'),
                "source_url": article_data.get('source_url'),
                "language": article_data.get('language')
            }

            # Only set status if explicitly provided, otherwise use database default
            if 'status' in article_data:
                insert_data['status'] = article_data['status']
            
            response = supabase.table("articles").insert(insert_data).execute()
            article_id = response.data[0]['id']
            # Insert into article_categories if category_id provided
            if article_data.get('category_id'):
                supabase.table("article_categories").insert({
                    "article_id": article_id,
                    "category_id": article_data['category_id']
                }).execute()
            return response.data[0]
        except Exception as e:
            raise e

    @staticmethod
    def approve_article(article_id: str):
        """Approve an article (admin only)"""
        try:
            response = supabase.table("articles").update({
                "status": "published",
                "published_at": "now()"
            }).eq("id", article_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise e

    @staticmethod
    def reject_article(article_id: str):
        """Reject an article (admin only)"""
        try:
            response = supabase.table("articles").update({
                "status": "rejected"
            }).eq("id", article_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise e

    @staticmethod
    def get_pending_articles():
        """Get all pending articles for admin review"""
        try:
            response = supabase.table("articles").select(
                "*, channels(name)"
            ).eq("status", "pending_review").order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def get_comments(article_id: str):
        try:
            # Get comments with basic data
            response = supabase.table("comments").select(
                "id, user_id, article_id, body, created_at"
            ).eq("article_id", article_id).order("created_at", desc=True).execute()

            comments = response.data
            if comments:
                # Get user IDs from comments
                user_ids = list(set([comment['user_id'] for comment in comments]))

                # Fetch profiles for these users
                profiles_response = supabase.table("profiles").select(
                    "user_id, display_name, avatar_url"
                ).in_("user_id", user_ids).execute()

                # Create a lookup map for profiles
                profiles_map = {profile['user_id']: profile for profile in profiles_response.data}

                # Attach profile info to each comment
                for comment in comments:
                    user_id = comment['user_id']
                    if user_id in profiles_map:
                        comment['profile'] = profiles_map[user_id]
                    else:
                        comment['profile'] = {'user_id': user_id, 'display_name': 'Anonymous', 'avatar_url': None}

            return comments
        except Exception as e:
            raise e

    @staticmethod
    def add_comment(article_id: str, comment_data: CommentCreate, user_id: str):
        try:
            response = supabase.table("comments").insert({
                "article_id": article_id,
                "user_id": user_id,
                "body": comment_data.content
            }).execute()
            return response.data[0]
        except Exception as e:
            raise e

    @staticmethod
    def bookmark_article(article_id: str, user_id: str):
        try:
            response = supabase.table("bookmarks").insert({
                "article_id": article_id,
                "user_id": user_id
            }).execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def remove_bookmark(article_id: str, user_id: str):
        try:
            response = supabase.table("bookmarks").delete().eq("article_id", article_id).eq("user_id", user_id).execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def get_user_bookmarks(user_id: str):
        try:
            response = supabase.table("bookmarks").select(
                "*, articles(*)"
            ).eq("user_id", user_id).execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def get_channels():
        try:
            response = supabase.table("channels").select("*").execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def publish_article(article_id: str):
        try:
            response = supabase.table("articles").update({
                "status": "published",
                "published_at": "now()"
            }).eq("id", article_id).eq("status", "pending_review").execute()
            if not response.data:
                raise Exception("Article not found or not in pending_review status")
            return response.data[0]
        except Exception as e:
            raise e

    @staticmethod
    def get_all_articles(page: int = 1, limit: int = 10):
        try:
            offset = (page - 1) * limit
            response = supabase.table("articles").select(
                "*, article_categories(*), channels(*)"
            ).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def update_article_status(article_id: str, status: str):
        try:
            response = supabase.table("articles").update({
                "status": status,
                "updated_at": "now()"
            }).eq("id", article_id).execute()
            if not response.data:
                raise Exception("Article not found")
            return response.data[0]
        except Exception as e:
            raise e

    @staticmethod
    def search_articles(query: str, page: int = 1, limit: int = 10):
        try:
            offset = (page - 1) * limit
            response = supabase.table("articles").select(
                "*, article_categories(*), channels(*)"
            ).ilike("title", f"%{query}%").eq("status", "published").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def subscribe_channel(channel_id: int, user_id: str):
        try:
            response = supabase.table("channel_subscriptions").insert({
                "channel_id": channel_id,
                "user_id": user_id
            }).execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def unsubscribe_channel(channel_id: int, user_id: str):
        try:
            response = supabase.table("channel_subscriptions").delete().eq("channel_id", channel_id).eq("user_id", user_id).execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def get_subscribed_channels(user_id: str):
        try:
            response = supabase.table("channel_subscriptions").select(
                "*, channels(*)"
            ).eq("user_id", user_id).execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def get_user_articles(user_id: str, page: int = 1, limit: int = 10):
        """Get all articles created by a specific user"""
        try:
            offset = (page - 1) * limit
            response = supabase.table("articles").select(
                "*, article_categories(*), channels(*)"
            ).eq("user_id", user_id).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            return response.data
        except Exception as e:
            raise e