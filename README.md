# News API

A simple FastAPI application with Supabase integration for news management.

## Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

## API Endpoints

### Health Check
- `GET /health` - Application health status

### Articles
- `GET /api/v1/articles?page=1&limit=10` - Get all articles with pagination
- `GET /api/v1/articles/{article_id}` - Get specific article details

### Categories
- `GET /api/v1/categories` - Get all categories

### Channels
- `GET /api/v1/channels` - Get all news channels

### Comments
- `GET /api/v1/articles/{article_id}/comments` - Get comments for an article

### Bookmarks
- `POST /api/v1/articles/{article_id}/bookmark` - Bookmark an article (requires user_id header)

## Database Schema

The API connects to an existing Supabase database with tables:
- `articles` - News articles with content, status, and metadata
- `categories` - Article categories with hierarchical structure
- `channels` - News sources and channels
- `comments` - Article comments system
- `bookmarks` - User bookmark system

## Features

- FastAPI with automatic OpenAPI documentation
- Supabase client for database operations
- CORS middleware for cross-origin requests
- Standardized JSON response format
- Error handling and validation
- Pagination support

## Environment Variables

Required environment variables are configured in `.env`:
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase public key

## Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.