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

For local Docker development, copy the override template and adjust it as needed for your machine:

```bash
cp docker-compose.override.example.yml docker-compose.override.yml
```

**Key Environment Variables:**

| Variable | Description | Example |
| :--- | :--- | :--- |
| `DEBUG` | Enable debug mode | `True` or `False` |
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | Database connection URL | `sqlite:///db.sqlite3` |
| `KEYCLOAK_INTROSPECT_URL` | OAuth2 Token Introspection URL | `http://auth-server/realms/master/protocol/openid-connect/token/introspect` |
| `KEYCLOAK_CLIENT_ID` | Client ID for introspection | `api-gateway` |
| `KEYCLOAK_CLIENT_SECRET` | Client Secret for introspection | `secret-value` |

### 3. Database Setup

Run migrations to set up the database (SQLite by default, or PostgreSQL if `DATABASE_URL` points to it):

```bash
poetry run python manage.py migrate
```

Examples:

```env
DATABASE_URL=sqlite:///db.sqlite3
DATABASE_URL=postgresql://user:password@localhost:5432/ninja_portal
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

For local development, Docker Compose will automatically load `docker-compose.override.yml` when present. Start from the versioned template:

```bash
cp docker-compose.override.example.yml docker-compose.override.yml
```

-   **API Gateway**: `http://localhost:8009` (Mapped port)
-   **Memcached**: Internal network.

---

## 📖 Usage & Architecture

### Dynamic Routing & Upstreams

The Gateway uses `Upstream` and `URIPattern` models to decide how to handle and route requests securely. You can manage these via the Django Admin interface (`/admin`).

**Upstream Fields:**
-   **Name**: A descriptive name for the partner service or backend.
-   **Base URL**: The base host URL for the destination (e.g., `https://api.partner.com/v1`).
-   **Application Token**: The token (API Key, service token) to inject in the outgoing request.
-   **Token Prefix**: The prefix for the authorization header (e.g., `Bearer `, `ApiKey `).

**URIPattern Fields:**
-   **URI Pattern**: The path pattern to match (e.g., `/api/v1/users`).
-   **Methods**: Comma-separated HTTP methods (e.g., `GET,POST`).
-   **Requires Auth**: Boolean. If `True`, the gateway validates the incoming client `Authorization` header against `KEYCLOAK_INTROSPECT_URL`.
-   **Upstream**: ForeignKey to the destination `Upstream` model.
-   **Target Path**: (Optional) Specific target URL or path override. If empty, the incoming path is appended to the `Upstream` Base URL.

### Request Flow

1.  **Client** sends a request to `/proxy/some/path`.
2.  **Gateway** matches the path against active `URIPatterns`.
    -   If no match found -> `403 Forbidden`.
3.  **Client Authentication** (if `Requires Auth` is True):
    -   Extracts client's `Bearer` token.
    -   Calls `KEYCLOAK_INTROSPECT_URL`.
    -   If invalid/inactive -> `401 Unauthorized`.
4.  **Forwarding & Upstream Auth**:
    -   Requests are forwarded to the linked `Upstream` backend URL.
    -   The `Upstream` mapped credentials (`Token Prefix` + `Application Token`) are injected into the `Authorization` header dynamically.
    -   Original headers (excluding Host, Content-Length, Authorization) are preserved.

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
