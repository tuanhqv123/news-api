from typing import List, Dict, Any, Optional
from ..config.database import supabase
from ..models.schemas import CategoryCreate, CategoryUpdate

class CategoryService:
    @staticmethod
    def create_category(category_data: dict, user_id: str) -> Dict[str, Any]:
        """Create a new category"""
        try:
            response = supabase.table("categories").insert({
                "name": category_data.get("name"),
                "slug": category_data.get("slug"),
                "description": category_data.get("description"),
                "parent_id": category_data.get("parent_id"),
                "created_at": "now()",
                "updated_at": "now()"
            }).execute()

            if response.data:
                return response.data[0]
            else:
                raise Exception("Failed to create category")
        except Exception as e:
            raise Exception(f"Error creating category: {str(e)}")

    @staticmethod
    def get_categories(page: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all categories with pagination"""
        try:
            # Calculate pagination
            offset = (page - 1) * limit

            response = supabase.table("categories")\
                .select("id, name, slug, description, parent_id, created_at, updated_at")\
                .order("created_at", desc=True)\
                .range(offset, limit)\
                .execute()

            return response.data
        except Exception as e:
            raise Exception(f"Error fetching categories: {str(e)}")

    @staticmethod
    def get_category(category_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific category by ID"""
        try:
            response = supabase.table("categories")\
                .select("id, name, slug, description, parent_id, created_at, updated_at")\
                .eq("id", category_id)\
                .single()\
                .execute()

            if response.data:
                return response.data
            else:
                return None
        except Exception as e:
            raise Exception(f"Error fetching category: {str(e)}")

    @staticmethod
    def update_category(category_id: int, category_data: dict, user_id: str) -> Dict[str, Any]:
        """Update an existing category"""
        try:
            response = supabase.table("categories")\
                .update({
                    "name": category_data.get("name"),
                    "slug": category_data.get("slug"),
                    "description": category_data.get("description"),
                    "parent_id": category_data.get("parent_id"),
                    "updated_at": "now()"
                })\
                .eq("id", category_id)\
                .execute()

            if response.data:
                return response.data[0]
            else:
                raise Exception("Failed to update category")
        except Exception as e:
            raise Exception(f"Error updating category: {str(e)}")

    @staticmethod
    def delete_category(category_id: int, user_id: str) -> bool:
        """Delete a category"""
        try:
            # Check if category has articles
            articles_response = supabase.table("articles")\
                .select("id")\
                .eq("category_id", category_id)\
                .execute()

            if articles_response.data and len(articles_response.data) > 0:
                raise Exception("Cannot delete category with existing articles")

            # Delete the category
            response = supabase.table("categories")\
                .delete()\
                .eq("id", category_id)\
                .execute()

            if not hasattr(response, 'error'):
                return True
            else:
                raise Exception("Failed to delete category")
        except Exception as e:
            raise Exception(f"Error deleting category: {str(e)}")