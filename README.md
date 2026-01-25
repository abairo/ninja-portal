# Ninja Portal (API Gateway)

Determine the routing, authentication, and proxying logic for your microservices architecture with **Ninja Portal** — a lightweight, asynchronous API Gateway built with **Django Ninja**.

## 🚀 Overview

**Ninja Portal** is designed to sit between your clients and your backend services. It provides:

-   **Dynamic Routing**: Define routing patterns in the database without restarting the service.
-   **Authentication & Authorization**: Validates Bearer tokens via introspection (e.g., Keycloak) before forwarding requests.
-   **High Performance Proxying**: Uses `aiohttp` for non-blocking, asynchronous request forwarding.
-   **Pattern Caching**: Uses Memcached to cache routing patterns for low-latency lookups.
-   **OpenAPI Documentation**: Automatic interactive API docs via Django Ninja.

## 🛠 Tech Stack

-   **Language**: Python 3.10+
-   **Framework**: [Django](https://www.djangoproject.com/) + [Django Ninja](https://django-ninja.rest-framework.com/)
-   **Async Client**: [aiohttp](https://docs.aiohttp.org/)
-   **Dependency Management**: [Poetry](https://python-poetry.org/)
-   **Database**: SQLite (default for dev), extensible to PostgreSQL/MySQL.
-   **Cache**: Memcached (using `pymemcache`).
-   **Containerization**: Docker & Docker Compose.

---

## ⚡ Quick Start

### Prerequisites

-   Python 3.10 or higher
-   [Poetry](https://python-poetry.org/docs/#installation)
-   Memcached (or Docker to run it)

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd ninja-portal
poetry install
```

### 2. Configuration

Copy the example environment file and configure it:

```bash
cp env.example .env
```

**Key Environment Variables:**

| Variable | Description | Example |
| :--- | :--- | :--- |
| `DEBUG` | Enable debug mode | `True` or `False` |
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `KEYCLOAK_INTROSPECT_URL` | OAuth2 Token Introspection URL | `http://auth-server/realms/master/protocol/openid-connect/token/introspect` |
| `KEYCLOAK_CLIENT_ID` | Client ID for introspection | `api-gateway` |
| `KEYCLOAK_CLIENT_SECRET` | Client Secret for introspection | `secret-value` |
| `BACKEND_BASE_URL` | Default fallback backend URL | `http://backend-service:8000` |
| `APP_TOKEN` | Token sent to backend services | `internal-service-token` |

### 3. Database Setup

Run migrations to set up the SQLite database (and create `URIPattern` table):

```bash
poetry run python manage.py migrate
```

### 4. Running the Development Server

Ensure Memcached is running (or use Docker, see below). Then:

```bash
poetry run python manage.py runserver
```

The server will start at `http://127.0.0.1:8000`.

---

## 🐳 Docker Deployment

You can run the entire stack (Gateway + Memcached) using Docker Compose:

```bash
docker-compose up -d --build
```

-   **API Gateway**: `http://localhost:8009` (Mapped port)
-   **Memcached**: Internal network.

---

## 📖 Usage & Architecture

### Dynamic Routing

The Gateway uses `URIPattern` models to decide how to handle requests. You can manage these via the Django Admin interface (`/admin`).

**Fields:**
-   **URI Pattern**: The path pattern to match (e.g., `/api/v1/users`).
-   **Methods**: Comma-separated HTTP methods (e.g., `GET,POST`).
-   **Requires Auth**: Boolean. If `True`, the gateway validates the `Authorization` header against `KEYCLOAK_INTROSPECT_URL`.
-   **Target Path**: (Optional) Specific target URL. If empty, it appends the incoming path to `BACKEND_BASE_URL`.

### Request Flow

1.  **Client** sends a request to `/proxy/some/path`.
2.  **Gateway** matches the path against active `URIPatterns`.
    -   If no match found -> `403 Forbidden`.
3.  **Authentication** (if `Requires Auth` is True):
    -   Extracts `Bearer` token.
    -   Calls `KEYCLOAK_INTROSPECT_URL`.
    -   If invalid/inactive -> `401 Unauthorized`.
4.  **Forwarding**:
    -   Requests are forwarded to the backend.
    -   An internal `Authorization: Token <APP_TOKEN>` header is injected.
    -   Original headers (excluding Host, Content-Length) are preserved.

### API Documentation

Interactive API documentation is automatically generated:

-   **Swagger UI**: `/docs`
-   **ReDoc**: `/redoc`

---

## 🧪 Testing

Run these tests to ensure everything is working correctly:

```bash
poetry run pytest
```