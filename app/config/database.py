from supabase import create_client, Client
from .settings import settings
import os

# Use SERVICE_ROLE_KEY for admin operations if available, otherwise use SUPABASE_KEY
service_role_key = settings.SERVICE_ROLE_KEY or settings.SUPABASE_KEY

# Main client for regular operations
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Admin client for admin operations
supabase_admin: Client = create_client(settings.SUPABASE_URL, service_role_key)