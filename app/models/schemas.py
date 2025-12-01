from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Response wrapper for consistent API responses
class StandardResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: str
    timestamp: datetime = datetime.now()

# Authentication schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

class AuthorInvite(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None
    channel_id: int

class UserInvite(BaseModel):
    email: EmailStr
    role_id: int
    channel_id: Optional[int] = None
    invited_by: str

# Article schemas
class ArticleCreate(BaseModel):
    title: str
    summary: str
    content: str
    category_id: int
    channel_id: Optional[int] = None
    source_url: Optional[str] = None
    hero_image_url: Optional[str] = None
    language: Optional[str] = None

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    channel_id: Optional[int] = None
    source_url: Optional[str] = None
    hero_image_url: Optional[str] = None
    language: Optional[str] = None
    published_at: Optional[datetime] = None

class CommentCreate(BaseModel):
    content: str

# Category schemas
class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

# Channel schemas
class ChannelCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    rss_url: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = True

class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    rss_url: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None

# Additional schemas
class BookmarkToggle(BaseModel):
    is_bookmarked: bool