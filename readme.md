# Furniture shop API
## Description

Basic REST API for furniture shop. Built on FastAPI and PostgreSQL. Runs in Docker. Also includes logging, and SMTP integration via MailHog.

## Stack

- **FastAPI** — REST API with auto-generated OpenAPI docs
- **PostgreSQL** + **SQLAlchemy** — persistence
- **Pydantic** — request/response schemas
- **MailHog** — SMTP server to catch order confirmation emails
- **Docker Compose** — the whole stack runs with one command

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/furniture/` | List all furniture, optionally filtered by `category` |
| `GET` | `/furniture/{id}` | Get a single item by ID |
| `GET` | `/orders/?q={email}` | List all orders placed by a customer, with items |
| `POST` | `/orders/` | Place an order and send a confirmation email |

Full interactive documentation is available at `/docs` once the app is running.


## Running

1. Install Docker Desktop
2. Clone the repository
3. Setup the database name and PostgreSQL password in the .env.example file and rename it to .env
4. Open project folder in terminal
5. Run `docker compose up --build`
6. Open:
- `http://localhost:8000/docs` for Swagger UI
- `http://localhost:8025/` for MailHog