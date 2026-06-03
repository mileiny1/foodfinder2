# FoodFinder API

FoodFinder is a Django REST API for user accounts and location-based restaurant search.
It supports JWT authentication, profile management, and food search powered by OpenAI (with a mock fallback mode for local development).

## Tech Stack

- Python 3.11
- Django
- Django REST Framework
- SimpleJWT (JWT auth)
- PostgreSQL
- Pipenv

## Features

- User registration with extended profile fields
- JWT login and refresh
- Authenticated profile read/update
- Authenticated food search by:
  - query
  - latitude/longitude
  - radius
  - min rating
  - open now
  - price range
- Search history per user
- Cached search results
- OpenAI-backed restaurant results with optional mock fallback

## Project Notes

This repository contains a nested `foodfinder/` directory that appears to duplicate parts of the project.
For normal development, use the root project where `manage.py` is in the repository root.

## Prerequisites

- Python 3.11
- Pipenv
- PostgreSQL running locally (or reachable over network)

## Environment Variables

Create a `.env` file in the repository root (same directory as `manage.py`):

```env
DJANGO_SECRET_KEY=dev-secret-change-me
DEBUG=1

DB_NAME=foodfinder
DB_USER=foodfinder
DB_PASSWORD=foodfinder
DB_HOST=127.0.0.1
DB_PORT=5432

# OpenAI
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini

# If true, API can return mock restaurant data when OpenAI is unavailable
ENABLE_MOCK_SEARCH_FALLBACK=1

# Optional cache backend (if unset, local in-memory cache is used)
# REDIS_URL=redis://127.0.0.1:6379/1

# Provider switch (current router path uses OpenAI)
PLACES_PROVIDER=yelp
```

## Local Setup

1. Install dependencies:

```bash
pipenv install
```

2. Activate virtual environment:

```bash
pipenv shell
```

3. Create PostgreSQL database and user (example):

```sql
CREATE DATABASE foodfinder;
CREATE USER foodfinder WITH PASSWORD 'foodfinder';
GRANT ALL PRIVILEGES ON DATABASE foodfinder TO foodfinder;
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Start development server:

```bash
python manage.py runserver
```

API base URL (default):

```text
http://127.0.0.1:8000/api/
```

## Running Tests

```bash
python manage.py test
```

## API Endpoints

### Public

- `GET /api/health/`
- `POST /api/auth/register/`
- `GET /api/auth/register/options/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`

### Authenticated (Bearer token required)

- `GET /api/auth/profile/`
- `PATCH /api/auth/profile/`
- `POST /api/food/search/`
- `GET /api/my-search-history/?limit=20`

## Auth Flow (Quick Start)

1. Register user
2. Login to receive tokens
3. Send `Authorization: Bearer <access_token>` for protected endpoints
4. Refresh token via `/api/auth/refresh/` when needed

## Example Requests

### Register

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securepass123",
    "confirm_password": "securepass123",
    "name": "New User",
    "home_address": "123 Main St",
    "birthday": "1996-07-20",
    "phone_number": "+1 555 101 2020",
    "gender": "female",
    "preferred_language": "es"
  }'
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser@example.com",
    "password": "securepass123"
  }'
```

### Food Search (Authenticated)

```bash
curl -X POST http://127.0.0.1:8000/api/food/search/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "query": "pizza",
    "lat": 37.7749,
    "lng": -122.4194,
    "radius_m": 3000,
    "limit": 10,
    "min_rating": 4.0,
    "open_now": true,
    "price_range": [1, 2]
  }'
```

### Get Search History
```bash
curl "http://127.0.0.1:8000/api/my-search-history/?limit=20" \
  -H "Authorization: Bearer <access_token>"
```
## Troubleshooting
- `OpenAI API key is missing`: set `OPENAI_API_KEY` or keep `ENABLE_MOCK_SEARCH_FALLBACK=1` for local mock results.
- Database connection errors: verify PostgreSQL credentials in `.env` and that PostgreSQL is running.
- 401 Unauthorized on protected routes: ensure `Authorization: Bearer <access_token>` is present and token is not expired.
