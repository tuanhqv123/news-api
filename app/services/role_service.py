from ..config.database import supabase
from typing import List, Dict, Any

class RoleService:
    @staticmethod
    def get_all_roles() -> List[Dict[str, Any]]:
        """Get all roles"""
        try:
            response = supabase.table("roles").select("*").order("id").execute()
            return response.data
        except Exception as e:
            raise e