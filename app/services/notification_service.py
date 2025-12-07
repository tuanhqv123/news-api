import firebase_admin
from firebase_admin import credentials, messaging
from typing import List, Optional, Dict, Any
from ..config.database import supabase
import json
import os

class NotificationService:
    _instance = None
    _app = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialize_firebase()
        return cls._instance

    @classmethod
    def _initialize_firebase(cls):
        """Initialize Firebase Admin SDK with HTTP v1"""
        try:
            if not firebase_admin._apps:
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                service_account_path = os.path.join(current_dir, '..', 'firebase-service-account.json')

                if os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                    options = {
                        'projectId': cred.project_id,
                        'messagingSenderId': '702340089040',
                    }
                    cls._app = firebase_admin.initialize_app(cred, options=options, name='news-api')
                elif os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON'):
                    service_account_info = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON'))
                    cred = credentials.Certificate(service_account_info)
                    options = {
                        'projectId': cred.project_id,
                        'messagingSenderId': '702340089040',
                    }
                    cls._app = firebase_admin.initialize_app(cred, options=options, name='news-api')
                else:
                    cls._app = None
        except Exception:
            cls._app = None

    def get_fcm_tokens_for_user(self, user_id: str) -> List[str]:
        """Get all FCM tokens for a specific user"""
        try:
            result = supabase.table("users_devices")\
                .select("fcm_token")\
                .eq("user_id", user_id)\
                .execute()

            tokens = [device["fcm_token"] for device in result.data]
            return [token for token in tokens
                   if token and not any(test in token.lower()
                   for test in ['test', 'mock', 'fake', 'demo'])]
        except Exception:
            return []

    def get_admin_fcm_tokens(self) -> List[str]:
        """Get all FCM tokens for admin users"""
        try:
            admin_result = supabase.table("profiles")\
                .select("user_id")\
                .eq("role_id", 1)\
                .execute()

            if not admin_result.data:
                return []

            admin_user_ids = [admin["user_id"] for admin in admin_result.data]

            tokens_result = supabase.table("users_devices")\
                .select("fcm_token")\
                .in_("user_id", admin_user_ids)\
                .execute()

            tokens = [device["fcm_token"] for device in tokens_result.data]
            return [token for token in tokens
                   if token and not any(test in token.lower()
                   for test in ['test', 'mock', 'fake', 'demo'])]
        except Exception:
            return []

    def send_notification(
        self,
        title: str,
        body: str,
        fcm_tokens: List[str],
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send notification to multiple FCM tokens using HTTP v1 multicast"""
        if not self._app or not fcm_tokens:
            return {"success": False, "message": "Firebase not initialized or no tokens"}

        MAX_TOKENS_PER_REQUEST = 500
        tokens_batches = [fcm_tokens[i:i + MAX_TOKENS_PER_REQUEST]
                         for i in range(0, len(fcm_tokens), MAX_TOKENS_PER_REQUEST)]

        total_success = 0
        total_failure = 0
        all_failed_tokens = []

        try:
            for tokens_batch in tokens_batches:
                message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                        image=image_url
                    ),
                    data=data or {},
                    tokens=tokens_batch,
                    android=messaging.AndroidConfig(
                        priority='high',
                        notification=messaging.AndroidNotification(
                            sound='default',
                            click_action='FLUTTER_NOTIFICATION_CLICK'
                        )
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                sound='default',
                                badge=1
                            )
                        )
                    )
                )

                response = messaging.send_each_for_multicast(message, app=self._app)

                total_success += response.success_count
                total_failure += response.failure_count

                if response.failure_count > 0:
                    for i, token in enumerate(tokens_batch):
                        if not response.responses[i].success:
                            all_failed_tokens.append(token)

            if all_failed_tokens:
                self._remove_invalid_tokens(all_failed_tokens)

            return {
                "success": total_success > 0,
                "success_count": total_success,
                "failure_count": total_failure,
                "total_batches": len(tokens_batches)
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def _remove_invalid_tokens(self, tokens: List[str]):
        """Remove invalid FCM tokens from database"""
        try:
            for token in tokens:
                supabase.table("users_devices")\
                    .delete()\
                    .eq("fcm_token", token)\
                    .execute()
        except Exception:
            pass

    def notify_admins_new_article(self, article_title: str, author_name: str, article_id: str):
        """Send notification to all admins when a new article is created"""
        admin_tokens = self.get_admin_fcm_tokens()

        if not admin_tokens:
            print("No admin tokens found")
            return

        return self.send_notification(
            title="📝 New Article Submitted",
            body=f"{author_name} submitted a new article: {article_title}",
            fcm_tokens=admin_tokens,
            data={
                "type": "new_article",
                "article_id": article_id,
                "action": "review"
            }
        )

    def notify_author_status_change(self, article_title: str, status: str, author_user_id: str, article_id: str):
        """Send notification to author when article status changes"""
        author_tokens = self.get_fcm_tokens_for_user(author_user_id)

        if not author_tokens:
            print(f"No tokens found for user {author_user_id}")
            return

        # Define status messages
        status_messages = {
            "published": "🎉 Your article has been published!",
            "rejected": "❌ Your article was rejected",
            "approved": "✅ Your article has been approved",
            "pending_review": "⏳ Your article is pending review"
        }

        status_message = status_messages.get(status, f"Your article status changed to: {status}")

        return self.send_notification(
            title=status_message,
            body=article_title,
            fcm_tokens=author_tokens,
            data={
                "type": "article_status_change",
                "article_id": article_id,
                "status": status
            }
        )

    def notify_admins_status_change(self, article_title: str, status: str, author_name: str, article_id: str):
        """Send notification to all admins when article status changes"""
        admin_tokens = self.get_admin_fcm_tokens()

        if not admin_tokens:
            print("No admin tokens found")
            return

        # Define admin status messages
        status_messages = {
            "published": "📢 Article Published",
            "rejected": "❌ Article Rejected",
            "approved": "✅ Article Approved",
            "pending_review": "⏳ Article Pending Review",
            "draft": "📝 Article Draft"
        }

        status_message = status_messages.get(status, f"Article status changed to: {status}")

        # Define body messages for admins
        body_messages = {
            "published": f"{author_name}'s article '{article_title}' is now live",
            "rejected": f"{author_name}'s article '{article_title}' was rejected",
            "approved": f"{author_name}'s article '{article_title}' has been approved",
            "pending_review": f"{author_name}'s article '{article_title}' is pending review",
            "draft": f"{author_name}'s article '{article_title}' is in draft"
        }

        body = body_messages.get(status, f"{author_name}'s article '{article_title}' status changed to {status}")

        return self.send_notification(
            title=status_message,
            body=body,
            fcm_tokens=admin_tokens,
            data={
                "type": "article_status_change",
                "article_id": article_id,
                "status": status
            }
        )

# Create singleton instance
notification_service = NotificationService()