from ..config.database import supabase
from typing import Dict, Any
import uuid

class MediaService:
    @staticmethod
    def upload_file(file_content: bytes, filename: str, content_type: str) -> str:
        """Upload file to Supabase storage bucket 'media' and return public URL"""
        try:
            # Generate unique filename
            file_extension = filename.split('.')[-1] if '.' in filename else ''
            unique_filename = f"{uuid.uuid4()}.{file_extension}"

            # Upload to Supabase storage
            bucket = supabase.storage.from_("media")
            response = bucket.upload(
                path=unique_filename,
                file=file_content,
                file_options={"content-type": content_type}
            )

            # If we reach here, upload was successful
            # Get public URL
            public_url = bucket.get_public_url(unique_filename)
            return public_url

        except Exception as e:
            raise e