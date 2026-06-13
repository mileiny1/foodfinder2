# FoodFinder API

> Django REST backend powering AI-assisted restaurant discovery with JWT authentication, location-based search, and optional OpenAI integration.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-REST%20Framework-092E20?style=flat&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=flat&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Example Requests](#example-requests)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)

---

## Overview

FoodFinder API is a Django REST backend that handles user authentication, profile management, and location-based restaurant search. It integrates with OpenAI to generate AI-backed restaurant recommendations and includes a mock fallback mode for local development.

The frontend counterpart is [AI FoodSearch](https://github.com/), a React + Vite app that communicates with this API.

---

## Features

- **Authentication** — JWT-based registration, login, and token refresh
- **Profile Management** — Extended user profiles with read and update support
- **Restaurant Search** — Location-aware search filtered by radius, rating, price range, and availability
- **AI Integration** — OpenAI-powered recommendations with configurable mock fallback
- **Search History** — Per-user search history tracking
- **Result Caching** — Optional Redis-backed response caching

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Framework | Django + Django REST Framework |
| Authentication | SimpleJWT |
| Database | PostgreSQL |
| AI Provider | OpenAI (gpt-4.1-mini) |
| Dependency Manager | Pipenv |
| Cache (optional) | Redis |

---

## Project Structure

```
foodfinder/                       # Project root
│
├── api/                          # Core Django application
│   ├── migrations/               # Database migrations
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   │
│   ├── services/                 # External service integrations
│   │   ├── __init__.py
│   │   ├── ai_openai.py          # OpenAI recommendation engine
│   │   ├── geo.py                # Geolocation utilities
│   │   ├── places_google.py      # Google Places integration
│   │   ├── places_router.py      # Provider routing logic
│   │   └── places_yelp.py        # Yelp integration
│   │
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── foodfinder/                   # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── .env                          # Environment variables (not committed)
├── .gitignore
├── LICENSE
├── manage.py
├── Pipfile
├── Procfile
├── requirements.txt
└── README.md
```

> **Note:** The repository contains a nested `foodfinder/` directory for Django project configuration. For all development, use the root `manage.py` — not any nested copy.

---

## Getting Started

### Prerequisites

- Python 3.11
- Pipenv
- PostgreSQL (running locally or accessible over the network)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/foodfinder-backend.git
cd foodfinder-backend
```

**2. Install dependencies**

```bash
pipenv install
pipenv shell
```

**3. Configure environment variables**

Copy the example below into a `.env` file at the project root (same directory as `manage.py`). See [Environment Variables](#environment-variables) for details.

**4. Set up the database**

```sql
CREATE DATABASE foodfinder;
CREATE USER foodfinder WITH PASSWORD 'foodfinder';
GRANT ALL PRIVILEGES ON DATABASE foodfinder TO foodfinder;
```

**5. Run migrations**

```bash
python manage.py migrate
```

**6. Start the development server**

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.

---

## Environment Variables

Create a `.env` file in the project root:

```env
# Django
DJANGO_SECRET_KEY=dev-secret-change-me
DEBUG=1

# Database
DB_NAME=foodfinder
DB_USER=foodfinder
DB_PASSWORD=foodfinder
DB_HOST=127.0.0.1
DB_PORT=5432

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4.1-mini

# Enable mock restaurant data when OpenAI is unavailable (local dev)
ENABLE_MOCK_SEARCH_FALLBACK=1

# Places provider
PLACES_PROVIDER=yelp

# Optional: Redis cache (falls back to in-memory if unset)
# REDIS_URL=redis://127.0.0.1:6379/1
```

---

## API Reference

### Public Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health/` | Health check |
| `POST` | `/api/auth/register/` | Register a new user |
| `GET` | `/api/auth/register/options/` | Retrieve registration field options |
| `POST` | `/api/auth/login/` | Log in and receive JWT tokens |
| `POST` | `/api/auth/refresh/` | Refresh an access token |

### Authenticated Endpoints

> All authenticated requests require the header: `Authorization: Bearer <access_token>`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/auth/profile/` | Retrieve the current user's profile |
| `PATCH` | `/api/auth/profile/` | Update the current user's profile |
| `POST` | `/api/food/search/` | Search for restaurants |
| `GET` | `/api/my-search-history/?limit=20` | Retrieve recent search history |

### Auth Flow

```
POST /api/auth/register/   →   Create account
POST /api/auth/login/      →   Receive access + refresh tokens
Authorization: Bearer ...  →   Include on all protected requests
POST /api/auth/refresh/    →   Get a new access token when expired
```

---

## Example Requests

### Register

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "confirm_password": "securepass123",
    "name": "Jane Doe",
    "home_address": "123 Main St",
    "birthday": "1996-07-20",
    "phone_number": "+1 555 101 2020",
    "gender": "female",
    "preferred_language": "en"
  }'
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "securepass123"
  }'
```

### Restaurant Search

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

---

## Running Tests

```bash
python manage.py test
```

---

## Troubleshooting

### Missing OpenAI API Key

If the application cannot reach OpenAI, verify `OPENAI_API_KEY` is set in your `.env`. For local development, set `ENABLE_MOCK_SEARCH_FALLBACK=1` to use mock restaurant data instead.

### Database Connection Errors

- Confirm PostgreSQL is running and reachable.
- Verify `DB_*` values in `.env` match your database configuration.
- Ensure all migrations have been applied (`python manage.py migrate`).

### 401 Unauthorized

- Include the `Authorization: Bearer <access_token>` header on all protected requests.
- Access tokens expire — use `POST /api/auth/refresh/` to get a new one.
- Confirm all auth-related environment variables are correctly configured.

### Works Locally but Fails in Production

This is most commonly caused by missing environment variables or unapplied migrations in the production environment. To resolve:

1. Review deployment and application logs to identify the failure.
2. Verify all environment variables match your production configuration.
3. Confirm database connectivity and apply any pending migrations.
4. Test API endpoints and external service integrations independently.
5. Redeploy after applying fixes.

---

## License

This project is licensed under the terms in [LICENSE](LICENSE).
