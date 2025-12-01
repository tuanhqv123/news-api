# News API Documentation

## Overview

This API provides endpoints for managing news articles, user authentication, categories, channels, and media uploads. It uses Supabase for backend services and FastAPI for the server.

**Base URL:** `http://localhost:8000` (change for production)

**Authentication:** Bearer token in Authorization header for protected endpoints.

**Response Format:** All responses follow this structure:

```json
{
  "success": true|false,
  "data": {...},
  "message": "string",
  "timestamp": "ISO 8601 datetime"
}
```

## Authentication Endpoints

### Register User

**Endpoint:** `POST /api/v1/auth/register`  
**Public:** Yes  
**Description:** Register a new user account.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "password123",
  "display_name": "User Name"
}
```

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "display_name": "User Name"
  }'
```

**Response (Success):**

```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "email": "user@example.com",
    "role": "reader",
    "message": "Please check your email to confirm your account"
  },
  "message": "User registered successfully. Please check your email to confirm your account.",
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

### Login

**Endpoint:** `POST /api/v1/auth/login`  
**Public:** Yes  
**Description:** Authenticate user and get tokens.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Response (Success):**

```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token",
    "refresh_token": "refresh_jwt_token",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "role": "reader",
      "display_name": "User Name",
      "avatar_url": null,
      "channel_id": null
    }
  },
  "message": "Login successful",
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

### Refresh Token

**Endpoint:** `POST /api/v1/auth/refresh`  
**Public:** No (requires valid refresh token)  
**Description:** Get new access token using refresh token.

**Request Body:**

```json
{
  "refresh_token": "your_refresh_token_here"
}
```

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_refresh_token_here"
  }'
```

**Response (Success):**

```json
{
  "success": true,
  "data": {
    "access_token": "new_jwt_token",
    "refresh_token": "new_refresh_jwt_token"
  },
  "message": "Token refreshed successfully",
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

### Logout

**Endpoint:** `POST /api/v1/auth/logout`  
**Public:** No  
**Description:** Logout user.

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (Success):**

```json
{
  "success": true,
  "data": null,
  "message": "Logout successful",
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

### Get Current User Profile

**Endpoint:** `GET /api/v1/auth/me`  
**Public:** No  
**Description:** Get current user profile.

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (Success):**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "role": "reader",
      "display_name": "User Name",
      "avatar_url": null,
      "channel_id": null
    }
  },
  "message": "User profile retrieved",
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

### Update Profile

**Endpoint:** `PUT /api/v1/auth/me`  
**Public:** No  
**Description:** Update user profile.

**Request Body:**

```json
{
  "display_name": "New Name",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

**Curl Example:**

```bash
curl -X PUT "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "New Name",
    "avatar_url": "https://example.com/avatar.jpg"
  }'
```

**Response (Success):**

```json
{
  "success": true,
  "data": null,
  "message": "Profile updated",
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

### Get Roles

**Endpoint:** `GET /api/v1/auth/roles`  
**Public:** No  
**Description:** Get all available roles.

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/auth/roles" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (Success):**

```json
{
  "success": true,
  "data": {
    "roles": [
      { "id": 1, "name": "admin" },
      { "id": 2, "name": "author" },
      { "id": 3, "name": "reader" }
    ]
  },
  "message": "Roles retrieved successfully",
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

### Invite User (Admin Only)

**Endpoint:** `POST /api/v1/auth/admin/invite-user`  
**Public:** No (Admin only)  
**Description:** Send invitation to new user.

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "role_id": 2,
  "channel_id": 1,
  "invited_by": "admin@example.com"
}
```

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/admin/invite-user" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "role_id": 2,
    "channel_id": 1,
    "invited_by": "admin@example.com"
  }'
```

**Response (Success):**

```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "email": "newuser@example.com",
    "role": "author",
    "message": "Invitation sent successfully"
  },
  "message": "User invitation sent successfully",
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

### Set User Role (Admin Only)

**Endpoint:** `POST /api/v1/auth/admin/set-role`  
**Public:** No (Admin only)  
**Description:** Change user's role.

**Query Parameters:**

- `user_id`: User ID to update
- `role`: New role (admin/author/reader)

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/admin/set-role?user_id=user_uuid&role=author" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (Success):**

```json
{
  "success": true,
  "data": {
    "user_id": "user_uuid",
    "role": "author"
  },
  "message": "User role updated to author",
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

## Article Endpoints

### Get Articles

**Endpoint:** `GET /api/v1/articles`  
**Public:** Yes  
**Description:** Get published articles with pagination.

**Query Parameters:**

- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `category`: Category ID filter (optional)

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/articles?page=1&limit=10&category=1"
```

**Response (Success):**

```json
{
  "success": true,
  "data": {
    "articles": [
      {
        "id": "uuid",
        "title": "Article Title",
        "summary": "Article summary",
        "content": "Full content",
        "category_id": 1,
        "channel_id": 1,
        "author_id": "uuid",
        "status": "published",
        "view_count": 100,
        "created_at": "2025-12-01T10:00:00.000000",
        "updated_at": "2025-12-01T10:00:00.000000"
      }
    ],
    "page": 1,
    "limit": 10
  },
  "message": "Articles retrieved",
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

### Get Article by ID

**Endpoint:** `GET /api/v1/articles/{article_id}`  
**Public:** Yes  
**Description:** Get specific published article.

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/articles/article_uuid"
```

**Response (Success):** Similar to above, single article object.

### Create Article (Author Only)

**Endpoint:** `POST /api/v1/articles`  
**Public:** No (Author only)  
**Description:** Create new article.

**Request Body:**

```json
{
  "title": "New Article",
  "summary": "Article summary",
  "content": "Full content",
  "category_id": 1,
  "source_url": "https://example.com",
  "hero_image_url": "https://example.com/image.jpg",
  "language": "en"
}
```

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/articles" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Article",
    "summary": "Article summary",
    "content": "Full content",
    "category_id": 1
  }'
```

**Response (Success):**

```json
{
  "success": true,
  "data": {
    "article": {
      "id": "uuid",
      "title": "New Article",
      "status": "published"
    }
  },
  "message": "Article created",
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

### Update Article (Author/Admin Only)

**Endpoint:** `PUT /api/v1/articles/{article_id}`  
**Public:** No  
**Description:** Update article.

**Request Body:** Same as create, all fields optional.

**Curl Example:**

```bash
curl -X PUT "http://localhost:8000/api/v1/articles/article_uuid" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title"
  }'
```

### Delete Article (Author/Admin Only)

**Endpoint:** `DELETE /api/v1/articles/{article_id}`  
**Public:** No  
**Description:** Delete article.

**Curl Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/articles/article_uuid" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Search Articles

**Endpoint:** `GET /api/v1/articles/search`  
**Public:** Yes  
**Description:** Search articles by query.

**Query Parameters:**

- `q`: Search query
- `page`: Page number
- `limit`: Items per page

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/articles/search?q=news&page=1&limit=10"
```

### Add Comment

**Endpoint:** `POST /api/v1/articles/{article_id}/comments`  
**Public:** No  
**Description:** Add comment to article.

**Request Body:**

```json
{
  "content": "This is a comment"
}
```

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/articles/article_uuid/comments" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a comment"
  }'
```

### Get Comments

**Endpoint:** `GET /api/v1/articles/{article_id}/comments`  
**Public:** Yes  
**Description:** Get article comments.

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/articles/article_uuid/comments"
```

### Bookmark Article

**Endpoint:** `POST /api/v1/articles/{article_id}/bookmark`  
**Public:** No  
**Description:** Bookmark article.

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/articles/article_uuid/bookmark" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Remove Bookmark

**Endpoint:** `DELETE /api/v1/articles/{article_id}/bookmark`  
**Public:** No  
**Description:** Remove bookmark.

**Curl Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/articles/article_uuid/bookmark" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## User Endpoints

### Get User Bookmarks

**Endpoint:** `GET /api/v1/users/me/bookmarks`  
**Public:** No  
**Description:** Get user's bookmarked articles.

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/users/me/bookmarks" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### List Users (Admin Only)

**Endpoint:** `GET /api/v1/users/admin/list`  
**Public:** No (Admin only)  
**Description:** Get all users.

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/users/admin/list" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Approve Author (Admin Only)

**Endpoint:** `PUT /api/v1/users/admin/approve-author/{user_id}`  
**Public:** No (Admin only)  
**Description:** Approve pending author.

**Curl Example:**

```bash
curl -X PUT "http://localhost:8000/api/v1/users/admin/approve-author/user_uuid" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Ban User (Admin Only)

**Endpoint:** `PUT /api/v1/users/admin/ban/{user_id}`  
**Public:** No (Admin only)  
**Description:** Ban user.

**Curl Example:**

```bash
curl -X PUT "http://localhost:8000/api/v1/users/admin/ban/user_uuid" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Unban User (Admin Only)

**Endpoint:** `PUT /api/v1/users/admin/unban/{user_id}`  
**Public:** No (Admin only)  
**Description:** Unban user.

**Curl Example:**

```bash
curl -X PUT "http://localhost:8000/api/v1/users/admin/unban/user_uuid" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Category Endpoints

### Get Categories

**Endpoint:** `GET /api/v1/categories`  
**Public:** Yes  
**Description:** Get all categories.

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/categories"
```

### Create Category (Admin Only)

**Endpoint:** `POST /api/v1/categories/admin/create`  
**Public:** No (Admin only)  
**Description:** Create new category.

**Request Body:**

```json
{
  "name": "Technology",
  "slug": "technology",
  "description": "Tech news",
  "parent_id": null
}
```

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/categories/admin/create" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Technology",
    "slug": "technology",
    "description": "Tech news"
  }'
```

### Update Category (Admin Only)

**Endpoint:** `PUT /api/v1/categories/admin/{category_id}`  
**Public:** No (Admin only)  
**Description:** Update category.

**Curl Example:**

```bash
curl -X PUT "http://localhost:8000/api/v1/categories/admin/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name"
  }'
```

### Delete Category (Admin Only)

**Endpoint:** `DELETE /api/v1/categories/admin/{category_id}`  
**Public:** No (Admin only)  
**Description:** Delete category.

**Curl Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/categories/admin/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Channel Endpoints

### Get Public Channels

**Endpoint:** `GET /api/v1/channels/public/list`  
**Public:** Yes  
**Description:** Get active channels.

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/channels/public/list"
```

### Get All Channels

**Endpoint:** `GET /api/v1/channels/list`
**Public:** No
**Description:** Get all channels.

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/channels/list" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Followed Channels

**Endpoint:** `GET /api/v1/channels/followed`
**Public:** No (Reader only)
**Description:** Get channels followed by the current user.

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/channels/followed" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (Success):**

```json
{
  "success": true,
  "data": {
    "channels": [
      {
        "id": 1,
        "name": "CNN",
        "slug": "cnn",
        "description": "CNN News",
        "rss_url": "https://rss.cnn.com/rss/edition.rss",
        "logo_url": "https://example.com/logo.jpg",
        "is_active": true,
        "created_at": "2025-12-01T10:00:00.000000"
      }
    ]
  },
  "message": "Followed channels retrieved successfully",
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

### Create Channel (Admin Only)

**Endpoint:** `POST /api/v1/channels/admin/create`  
**Public:** No (Admin only)  
**Description:** Create new channel.

**Request Body:**

```json
{
  "name": "CNN",
  "slug": "cnn",
  "description": "CNN News",
  "rss_url": "https://rss.cnn.com/rss/edition.rss",
  "logo_url": "https://example.com/logo.jpg"
}
```

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/channels/admin/create" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CNN",
    "slug": "cnn",
    "description": "CNN News"
  }'
```

### Update Channel (Admin Only)

**Endpoint:** `PUT /api/v1/channels/admin/{channel_id}`  
**Public:** No (Admin only)  
**Description:** Update channel.

**Curl Example:**

```bash
curl -X PUT "http://localhost:8000/api/v1/channels/admin/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name"
  }'
```

### Delete Channel (Admin Only)

**Endpoint:** `DELETE /api/v1/channels/admin/{channel_id}`  
**Public:** No (Admin only)  
**Description:** Delete channel.

**Curl Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/channels/admin/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Follow Channel

**Endpoint:** `POST /api/v1/channels/{channel_id}/follow`  
**Public:** No (Reader only)  
**Description:** Follow channel.

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/channels/1/follow" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Unfollow Channel

**Endpoint:** `DELETE /api/v1/channels/{channel_id}/follow`  
**Public:** No (Reader only)  
**Description:** Unfollow channel.

**Curl Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/channels/1/follow" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Media Endpoints

### Upload File

**Endpoint:** `POST /api/v1/media/upload`  
**Public:** No (Author/Reader only)  
**Description:** Upload file to media storage.

**Request:** Multipart form data with file.

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/media/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/file.jpg"
```

**Response (Success):**

```json
{
  "success": true,
  "data": {
    "url": "https://supabase-url/storage/v1/object/public/media/uuid.jpg"
  },
  "message": "File uploaded successfully",
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

## Root Endpoints

### Health Check

**Endpoint:** `GET /health`  
**Public:** Yes  
**Description:** Check API health.

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Root

**Endpoint:** `GET /`  
**Public:** Yes  
**Description:** Basic API info.

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/"
```

**Response:**

```json
{
  "message": "News API is running"
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  },
  "timestamp": "2025-12-01T10:00:00.000000"
}
```

Common HTTP status codes:

- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `500`: Internal Server Error

## Authentication Notes

- Use `Bearer YOUR_ACCESS_TOKEN` in Authorization header for protected endpoints.
- Tokens expire after 1 hour; use refresh endpoint to get new ones.
- Admin endpoints require admin role.
- Author endpoints require author role.
- Reader endpoints require reader role.
- Some endpoints allow author or reader roles.
