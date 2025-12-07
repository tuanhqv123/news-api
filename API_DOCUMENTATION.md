# News API Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [User Roles & Permissions](#user-roles--permissions)
3. [Authentication APIs](#authentication-apis)
4. [User Management APIs](#user-management-apis)
5. [Article Management APIs](#article-management-apis)
6. [Channel Management APIs](#channel-management-apis)
7. [Category Management APIs](#category-management-apis)
8. [Media APIs](#media-apis)
9. [Notification APIs](#notification-apis)
10. [User Stories & Workflows](#user-stories--workflows)
10. [Error Handling](#error-handling)

---

## 🎯 Overview

The News API is a comprehensive content management system designed for news publishing with role-based access control. It enables administrators to manage users, content, and channels while providing authors with tools to create and publish articles.

### Key Features
- **Role-Based Access Control** (Admin, Author, Reader)
- **User Invitation System** with role assignment
- **Article Management** with approval workflows
- **Channel & Category Organization**
- **Media Upload & Management**
- **User Management** (ban/unban, role changes)
- **Push Notifications** with device token management

### Base Configuration
- **Base URL**: `http://localhost:8000` (production: `https://your-domain.com`)
- **Authentication**: Bearer token in Authorization header
- **Response Format**: Standardized JSON responses
- **API Version**: v1

---

## 👥 User Roles & Permissions

### 🔐 **Admin Role**
**Permissions**: Full system access
- ✅ Invite users with specific roles
- ✅ View and manage all users
- ✅ Ban/unban users
- ✅ Change user roles
- ✅ Approve/reject articles
- ✅ Manage channels and categories
- ✅ View all analytics and reports

**User Story**: As a **system administrator**, I need to manage the entire platform, invite team members, and ensure content quality by controlling who can publish and manage content.

### ✍️ **Author Role**
**Permissions**: Content creation and management
- ✅ Create and edit own articles
- ✅ Submit articles for review
- ✅ Publish approved articles
- ✅ View own analytics
- ✅ Upload media for articles
- ✅ Comment on articles

**User Story**: As an **author**, I need to write compelling news articles, upload supporting media, and publish content that reaches our readers while following editorial guidelines.

### 👁️ **Reader Role**
**Permissions**: Content consumption and interaction
- ✅ View published articles
- ✅ Bookmark articles
- ✅ Comment on articles
- ✅ Follow channels
- ✅ Search articles
- ✅ View user profiles

**User Story**: As a **reader**, I want to discover interesting news content, save articles for later, engage with the community through comments, and follow my favorite channels.

---

## 🔐 Authentication APIs

### **POST /api/v1/auth/register**
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "display_name": "John Doe"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "role": "reader",
      "display_name": "John Doe"
    }
  },
  "message": "Registration successful"
}
```

**Use Case**: New users can register themselves with automatic "reader" role assignment.

---

### **POST /api/v1/auth/login**
Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "admin@gmail.com",
  "password": "test123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "abc123",
    "user": {
      "id": "2cba8b46-ed8a-4510-a7dd-7b8c57cce84a",
      "email": "admin@gmail.com",
      "role": "admin",
      "display_name": "admin"
    }
  },
  "message": "Login successful"
}
```

**Use Case**: Users authenticate to access role-protected features.

---

### **POST /api/v1/auth/admin/invite-user** ⭐
**Admin Only**: Invite users with specific roles.

**Request Body:**
```json
{
  "email": "newauthor@example.com",
  "role_id": 2,
  "channel_id": null,
  "invited_by": "admin@gmail.com"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "62c6d89c-fc87-44b2-949e-54d6069b7d84",
    "email": "newauthor@example.com",
    "role": "author",
    "message": "Invitation sent successfully"
  },
  "message": "User invitation sent successfully"
}
```

**Role ID Mapping:**
- `1` = Admin
- `2` = Author
- `3` = Reader

**Business Value**: Streamlines team onboarding by allowing admins to invite users with pre-assigned roles, eliminating manual approval workflows.

---

## 👥 User Management APIs

### **GET /api/v1/users/admin/all-profiles** ⭐
**Admin Only**: View all user profiles with optional filtering.

**Query Parameters:**
- `role` (optional): Filter by role name ("admin", "author", "reader")

**Response:**
```json
{
  "success": true,
  "data": {
    "profiles": [
      {
        "user_id": "uuid",
        "display_name": "John Doe",
        "email": "john@example.com",
        "role_id": 2,
        "roles": {
          "name": "author",
          "description": "Can create and manage own articles"
        },
        "created_at": "2025-01-01T00:00:00Z",
        "banned_until": null,
        "is_super_admin": false
      }
    ]
  },
  "message": "User profiles retrieved"
}
```

**Use Cases:**
- View all users: `GET /api/v1/users/admin/all-profiles`
- Filter authors only: `GET /api/v1/users/admin/all-profiles?role=author`
- Filter readers only: `GET /api/v1/users/admin/all-profiles?role=reader`

**Business Value**: Provides comprehensive user management dashboard with real-time filtering capabilities.

---

### **PUT /api/v1/users/admin/set-role/{user_id}** ⭐
**Admin Only**: Change a user's role.

**Request Body:**
```json
{
  "role": "author"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User role updated to author"
}
```

**Business Value**: Enables dynamic role management as team members change responsibilities or get promoted.

---

### **PUT /api/v1/users/admin/ban/{user_id}** ⭐
**Admin Only**: Ban a user for 100 years (effectively permanent).

**Response:**
```json
{
  "success": true,
  "message": "User banned successfully"
}
```

**Business Value**: Protects platform integrity by removing problematic users while maintaining their data for compliance.

---

### **PUT /api/v1/users/admin/unban/{user_id}** ⭐
**Admin Only**: Remove ban from a user.

**Response:**
```json
{
  "success": true,
  "message": "User unbanned successfully"
}
```

**Business Value**: Allows for user rehabilitation and appeals process.

---

## 📰 Article Management APIs

### **GET /api/v1/articles/**
Get published articles with pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "articles": [
      {
        "id": "uuid",
        "title": "Breaking News Story",
        "summary": "A compelling summary",
        "content": "Full article content...",
        "hero_image_url": "https://example.com/image.jpg",
        "published_at": "2025-01-01T00:00:00Z",
        "view_count": 1500,
        "author": {
          "display_name": "John Doe",
          "avatar_url": "https://example.com/avatar.jpg"
        },
        "categories": ["Technology", "AI"],
        "channel": {
          "name": "Tech News",
          "slug": "tech-news"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 100,
      "pages": 10
    }
  },
  "message": "Articles retrieved successfully"
}
```

**Business Value**: Powers the main content discovery engine for readers.

---

### **POST /api/v1/articles/** ⭐
**Author Only**: Create a new article.

**Request Body:**
```json
{
  "title": "New Article Title",
  "summary": "Article summary",
  "content": "Full article content...",
  "category_ids": [1, 2, 3],
  "hero_image_url": "https://example.com/image.jpg",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "article": {
      "id": "uuid",
      "title": "New Article Title",
      "status": "pending_review",
      "created_at": "2025-01-01T00:00:00Z"
    }
  },
  "message": "Article created successfully"
}
```

**Business Value**: Enables authors to create content that goes through editorial review before publication.

---

### **PUT /api/v1/articles/{article_id}/publish** ⭐
**Author Only**: Publish an approved article.

**Response:**
```json
{
  "success": true,
  "message": "Article published successfully"
}
```

**Business Value**: Gives authors control over when their approved content goes live.

---

### **GET /api/v1/articles/search** ⭐
Search articles by keyword.

**Query Parameters:**
- `q`: Search query
- `page`: Page number
- `limit`: Items per page

**Business Value**: Enhances content discoverability for readers.

---

## 📺 Channel Management APIs

### **POST /api/v1/channels/admin/create** ⭐
**Admin Only**: Create a new content channel.

**Request Body:**
```json
{
  "name": "Technology News",
  "slug": "tech-news",
  "description": "Latest tech news and updates",
  "logo_url": "https://example.com/logo.jpg",
  "rss_url": "https://example.com/rss.xml"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "channel": {
      "id": 1,
      "name": "Technology News",
      "slug": "tech-news",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  },
  "message": "Channel created successfully"
}
```

**Business Value**: Organizes content into logical categories for better navigation and brand management.

---

### **GET /api/v1/channels/public/list** ⭐
Get all active channels for public consumption.

**Response:**
```json
{
  "success": true,
  "data": {
    "channels": [
      {
        "id": 1,
        "name": "Technology News",
        "slug": "tech-news",
        "description": "Latest tech news",
        "logo_url": "https://example.com/logo.jpg",
        "follower_count": 5000,
        "article_count": 150
      }
    ]
  },
  "message": "Channels retrieved successfully"
}
```

**Business Value**: Enables content discovery through channel browsing.

---

## 🏷️ Category Management APIs

### **POST /api/v1/categories/admin/create** ⭐
**Admin Only**: Create a new category.

**Request Body:**
```json
{
  "name": "Artificial Intelligence",
  "slug": "artificial-intelligence",
  "description": "AI news and developments",
  "parent_id": null
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "category": {
      "id": 1,
      "name": "Artificial Intelligence",
      "slug": "artificial-intelligence",
      "created_at": "2025-01-01T00:00:00Z"
    }
  },
  "message": "Category created successfully"
}
```

**Business Value**: Provides granular content categorization for improved content discovery and SEO.

---

## 📸 Media APIs

### **POST /api/v1/media/upload** ⭐
**Author/Reader Only**: Upload media files.

**Request:** Multipart form with file data

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://example.com/media/image.jpg",
    "filename": "image.jpg",
    "size": 1024000,
    "content_type": "image/jpeg"
  },
  "message": "File uploaded successfully"
}
```

**Business Value**: Enables rich content creation with images and media support.

---

## 🔔 Notification APIs

### **POST /api/v1/notifications/set-token** ⭐
**Public Endpoint**: Set/update a device token for push notifications. Handles both guest users and logged-in users.

**Request:**
```json
{
  "fcm_token": "firebase_cloud_messaging_token_string",
  "device_type": "android",
  "user_id": "user_uuid_or_null"
}
```

**Request Details:**
- `fcm_token` (required): Firebase Cloud Messaging token
- `device_type` (optional): Device type (android, ios, web). Default: "android"
- `user_id` (optional): User UUID from auth.users or null for guest users

**Examples:**

Guest User Registration:
```json
{
  "fcm_token": "token_123",
  "device_type": "android",
  "user_id": null
}
```

User Login Update:
```json
{
  "fcm_token": "token_123",
  "device_type": "android",
  "user_id": "62c6d89c-fc87-44b2-949e-54d6069b7d84"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Device token set successfully"
}
```

**Business Value**: Enables push notifications for all users with dynamic user_id management. Supports guest-to-user transitions, multi-device support, and automatic token updates.

### **GET /api/v1/notifications/my-devices** ⭐
**Public Endpoint**: Get devices for a specific user or all guest devices.

**Query Parameters:**
- `user_id` (optional): User UUID to filter devices. If not provided, returns guest devices only

**Examples:**
- `GET /api/v1/notifications/my-devices` - Returns all guest devices
- `GET /api/v1/notifications/my-devices?user_id=uuid` - Returns devices for specific user

**Response:**
```json
{
  "success": true,
  "data": {
    "devices": [
      {
        "fcm_token": "token_string",
        "device_type": "android",
        "created_at": "2025-01-01T00:00:00Z",
        "last_used_at": "2025-01-01T12:00:00Z"
      }
    ]
  },
  "message": "Devices retrieved successfully"
}
```

**Business Value**: Allows users and administrators to view registered devices per user, useful for debugging notification issues and managing multi-device scenarios.

### **POST /api/v1/auth/logout** (Updated)
**Authenticated Users Only**: Logout user and optionally set device token to guest mode.

**Request:**
```json
{
  "fcm_token": "optional_device_token_to_reset"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

**Business Value**: Enables proper session management with automatic guest mode conversion for devices, ensuring users receive appropriate notifications based on their authentication state.

---

## 🎭 User Stories & Workflows

### **Administrator Workflow**

#### **Story**: As a platform administrator, I need to build and manage my news team efficiently.

**Workflow:**
1. **Onboarding New Authors**
   ```
   POST /api/v1/auth/admin/invite-user
   {
     "email": "journalist@news.com",
     "role_id": 2,  // Author role
     "invited_by": "admin@news.com"
   }
   ```
   **Value**: Streamlined team expansion without manual approval processes.

2. **Managing Team Performance**
   ```
   GET /api/v1/users/admin/all-profiles?role=author
   ```
   - Review all author activity
   - Monitor content quality
   - Identify top performers

3. **Content Quality Control**
   ```
   GET /api/v1/articles/admin/pending
   PUT /api/v1/articles/admin/approve/{article_id}
   PUT /api/v1/articles/admin/reject/{article_id}
   ```
   - Ensure editorial standards
   - Maintain brand voice consistency

4. **User Management**
   ```
   PUT /api/v1/users/admin/set-role/{user_id}  // Promote authors
   PUT /api/v1/users/admin/ban/{user_id}       // Remove problematic users
   ```
   - Dynamic team restructuring
   - Platform safety and compliance

### **Author Workflow**

#### **Story**: As a journalist, I need to create, edit, and publish engaging news content efficiently.

**Workflow:**
1. **Content Creation**
   ```
   POST /api/v1/articles/
   {
     "title": "Breaking: Major Tech Announcement",
     "summary": "Company reveals revolutionary product...",
     "content": "Full article with rich formatting...",
     "category_ids": [1, 5],
     "hero_image_url": "https://example.com/hero.jpg"
   }
   ```

2. **Media Management**
   ```
   POST /api/v1/media/upload
   // Upload images, videos, infographics
   ```

3. **Publication Process**
   ```
   PUT /api/v1/articles/{article_id}/publish
   // Publish approved content
   ```

4. **Performance Tracking**
   ```
   GET /api/v1/articles/my-articles
   // Monitor view counts, engagement metrics
   ```

**Business Value**: Empowers journalists to focus on content quality while maintaining editorial workflows.

### **Reader Workflow**

#### **Story**: As a news consumer, I want to discover relevant content and engage with the community.

**Workflow:**
1. **Content Discovery**
   ```
   GET /api/v1/articles/              // Browse latest articles
   GET /api/v1/articles/search?q=AI   // Search specific topics
   GET /api/v1/channels/public/list   // Discover channels
   ```

2. **Personalization**
   ```
   POST /api/v1/articles/{article_id}/bookmark  // Save for later
   POST /api/v1/channels/{channel_id}/follow     // Follow favorite topics
   ```

3. **Community Engagement**
   ```
   POST /api/v1/articles/{article_id}/comments
   {
     "body": "Great article! Very insightful analysis..."
   }
   ```

**Business Value**: Creates engaging user experience that drives return visits and community growth.

---

## 🎯 Business Value & ROI

### **Operational Efficiency**
- **Reduced Onboarding Time**: 80% faster team member addition through invitation system
- **Automated Workflows**: Editorial approval processes eliminate manual bottlenecks
- **Scalable Architecture**: Role-based system supports unlimited team growth

### **Content Quality Assurance**
- **Editorial Control**: Admin approval ensures brand consistency
- **Role-Based Permissions**: Prevents unauthorized content changes
- **Audit Trail**: Complete user action tracking for compliance

### **User Experience Optimization**
- **Seamless Discovery**: Advanced search and categorization
- **Personalization**: Bookmarking and channel following
- **Community Features**: Comments and engagement metrics

### **Technical Benefits**
- **RESTful Design**: Clean, predictable API structure
- **Role-Based Security**: Granular permission control
- **Scalable Architecture**: Cloud-native with Supabase
- **Real-time Updates**: Live content publishing and updates

---

## ❌ Error Handling

### **Standard Error Response Format**
```json
{
  "detail": "Error message describing what went wrong"
}
```

### **Common HTTP Status Codes**
- `200`: Success
- `201`: Created (resource successfully created)
- `400`: Bad Request (invalid input data)
- `401`: Unauthorized (invalid or missing authentication)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error (unexpected server error)

### **Authentication Errors**
```json
{
  "detail": "Authentication failed: Invalid token"
}
```

### **Permission Errors**
```json
{
  "detail": "Access forbidden. Admin role required."
}
```

### **Validation Errors**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🚀 Getting Started

### **Setup Requirements**
1. Admin account with credentials
2. Supabase project configuration
3. API access token from authentication

### **Quick Start Guide**
1. **Authenticate as Admin**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@gmail.com", "password": "test123"}'
   ```

2. **Invite First Author**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/admin/invite-user" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"email": "author@example.com", "role_id": 2, "invited_by": "admin@gmail.com"}'
   ```

3. **Create Channel**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/channels/admin/create" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "Technology News", "slug": "tech-news"}'
   ```

### **Rate Limiting**
- API endpoints are rate-limited to prevent abuse
- Standard limits: 100 requests per minute per user
- Admin endpoints: 50 requests per minute

### **Support & Documentation**
For technical support and questions:
- Review this documentation for common use cases
- Check error messages for debugging guidance
- Contact development team for feature requests

---

*Last Updated: December 2025*
*API Version: v1.0*