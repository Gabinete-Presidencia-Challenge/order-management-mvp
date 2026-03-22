# Order Management Platform — MVP

Internal order management platform built with a **microservices** backend (FastAPI + Python) and **microfrontends** (React + Webpack Module Federation).

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Frontend — Webpack Module Federation                        │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  Shell / Host    │  │   Orders MFE     │                 │
│  │  (port 3000)     │  │   (port 3001)    │                 │
│  │  routing, auth   │  │   list/filter/   │                 │
│  │  layout, context │  │   create orders  │                 │
│  └─────────┬────────┘  └────────┬─────────┘                 │
└────────────┼────────────────────┼──────────────────────────-┘
             │                    │  (Module Federation)
             ▼                    ▼
┌──────────────────────────────────────────────────────────────┐
│  API Gateway — Nginx (port 8080)                             │
│  /api/orders/*  →  orders-service                           │
│  /api/users/*   →  users-service                            │
└──────┬──────────────────────┬───────────────────────────────┘
       │                      │
       ▼                      ▼
┌─────────────────┐  ┌─────────────────┐
│  Orders Service │  │  Users Service  │
│  FastAPI :8001  │  │  FastAPI :8002  │
│  CRUD orders    │  │  Auth / JWT     │
│  status history │  │  user mgmt      │
└────────┬────────┘  └────────┬────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐   ┌─────────────────┐
│  orders_db      │  │  users_db       │   │  Redis          │
│  PostgreSQL     │  │  PostgreSQL     │   │  cache/session  │
│  :5432          │  │  :5433          │   │  :6379          │
└─────────────────┘  └─────────────────┘   └─────────────────┘
```

Each microservice owns its database exclusively. Services never share a database connection or schema.

---

## Project structure

```
order-management-mvp/
├── services/
│   ├── orders-service/          # FastAPI — order CRUD + status history
│   │   ├── app/
│   │   │   ├── api/endpoints/   # orders.py router
│   │   │   ├── core/            # config.py
│   │   │   ├── db/              # session.py
│   │   │   ├── models/          # SQLAlchemy — Order, OrderItem, OrderStatusHistory
│   │   │   ├── schemas/         # Pydantic I/O schemas
│   │   │   ├── services/        # order_service.py (business logic)
│   │   │   └── tests/           # test_orders.py (unit tests)
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── users-service/           # FastAPI — user management + JWT auth
│       ├── app/
│       │   ├── api/endpoints/   # auth.py, users.py routers
│       │   ├── core/            # config.py, security.py
│       │   ├── db/              # session.py
│       │   ├── models/          # SQLAlchemy — User
│       │   ├── schemas/         # Pydantic I/O schemas
│       │   ├── services/        # user_service.py
│       │   └── tests/           # test_users.py (unit tests)
│       ├── Dockerfile
│       └── requirements.txt
│
├── frontend/
│   ├── shell-app/               # Host MFE — routing, auth context, layout
│   │   ├── src/
│   │   │   ├── App.jsx
│   │   │   ├── contexts/AuthContext.jsx
│   │   │   └── components/     # Layout.jsx, LoginPage.jsx
│   │   ├── webpack.config.js   # ModuleFederationPlugin (host)
│   │   └── Dockerfile
│   │
│   └── orders-mfe/              # Orders MFE — exposed remote
│       ├── src/
│       │   ├── OrdersApp.jsx    # exposed entry point
│       │   ├── components/     # OrdersListPage, OrderDetailPage, OrderCreatePage
│       │   ├── hooks/          # useOrders.js
│       │   └── services/       # ordersApi.js
│       ├── webpack.config.js   # ModuleFederationPlugin (remote)
│       └── Dockerfile
│
├── nginx/
│   └── nginx.conf               # API gateway routing rules
│
├── .github/
│   └── workflows/
│       ├── orders-service-ci.yml
│       ├── users-service-ci.yml
│       └── frontend-ci.yml
│
└── docker-compose.yml           # Full stack — single command startup
```

---

## Running the stack

### Prerequisites

- Docker ≥ 24 and Docker Compose v2
- Ports 8080, 8001, 8002, 5432, 5433, 6379 available on the host

### Start everything

```bash
git clone <repository-url>
cd order-management-mvp

docker-compose up --build
```

This single command starts: `orders-db`, `users-db`, `redis`, `orders-service`, `users-service`, `shell-app`, `orders-mfe`, `api-gateway`.

| Service         | URL                                      |
|-----------------|------------------------------------------|
| Platform UI     | http://localhost:8080                    |
| Orders API docs | http://localhost:8001/docs               |
| Users API docs  | http://localhost:8002/docs               |
| Orders service  | http://localhost:8001/health             |
| Users service   | http://localhost:8002/health             |

### Stop the stack

```bash
docker-compose down           # stop containers, keep volumes
docker-compose down -v        # stop and delete all data volumes
```

---

## Running tests locally

### Orders service

```bash
cd services/orders-service
pip install -r requirements.txt
pytest app/tests/ -v
```

### Users service

```bash
cd services/users-service
pip install -r requirements.txt
pytest app/tests/ -v
```

Tests use SQLite in-memory databases — no external PostgreSQL required to run the test suite.

---

## API reference

### Orders service (port 8001)

| Method | Path                          | Description                    |
|--------|-------------------------------|--------------------------------|
| GET    | /api/v1/orders                | List orders (filter, paginate) |
| POST   | /api/v1/orders                | Create a new order             |
| GET    | /api/v1/orders/{id}           | Get order detail + history     |
| PATCH  | /api/v1/orders/{id}/status    | Update order status            |
| DELETE | /api/v1/orders/{id}           | Delete an order                |
| GET    | /health                       | Health check                   |

Order statuses: `pending` → `confirmed` → `processing` → `shipped` → `delivered` / `cancelled`

### Users service (port 8002)

| Method | Path                    | Description               |
|--------|-------------------------|---------------------------|
| POST   | /api/v1/auth/register   | Register a new user       |
| POST   | /api/v1/auth/login      | Authenticate, get JWT     |
| GET    | /api/v1/users           | List users                |
| POST   | /api/v1/users           | Create user (admin)       |
| GET    | /api/v1/users/{id}      | Get user by ID            |
| PATCH  | /api/v1/users/{id}      | Update user               |
| DELETE | /api/v1/users/{id}      | Delete user               |
| GET    | /health                 | Health check              |

User roles: `admin`, `operator`, `viewer`

---

## CI Pipeline

Three GitHub Actions workflows fire on push/PR when files in the relevant service change:

| Workflow                    | Trigger path                | Jobs                          |
|-----------------------------|-----------------------------|-------------------------------|
| `orders-service-ci.yml`     | `services/orders-service/**`| test → lint (ruff) → docker build |
| `users-service-ci.yml`      | `services/users-service/**` | test → lint (ruff) → docker build |
| `frontend-ci.yml`           | `frontend/**`               | build shell-app, build orders-mfe, verify remoteEntry.js |

Path-scoped triggers mean that a push touching only the orders service does not run the users service or frontend pipeline — each service owns its CI independently.

---

## Technical decisions

### Backend

**FastAPI** was chosen over Django REST Framework or Flask because it provides native async support, automatic OpenAPI documentation generation, and first-class Pydantic integration — reducing boilerplate significantly for a microservices context where each service needs well-defined contracts at its boundaries.

**Database-per-service** is the core data isolation pattern. `orders-db` and `users-db` are separate PostgreSQL instances running in separate containers. No service accesses another service's database directly; inter-service communication happens only through HTTP APIs. This allows each service to evolve its schema independently.

**SQLAlchemy + Alembic** for ORM and migrations. Alembic migration directories are scaffolded in each service; in this MVP the tables are created via `metadata.create_all` on startup for simplicity, with Alembic ready to be activated for production migration management.

**Redis** is included as a complementary non-relational layer. In this MVP it is provisioned and wired; in the next iteration it would be used for distributed session storage (users-service), idempotency keys on order creation, and as a cache layer for frequently-queried product/catalog data.

**JWT-based authentication** in the users-service. Tokens carry `sub` (user ID), `email`, and `role`. In this MVP the orders-service does not yet validate tokens (it trusts the gateway); a production hardening step would add JWT verification middleware in each downstream service.

### Frontend

**Webpack Module Federation** (built into Webpack 5) was chosen as the MFE composition mechanism. It allows each MFE to be built, deployed, and versioned independently while sharing singleton React and React Router instances at runtime — avoiding duplicate bundle weight and context isolation problems that arise from naive iframe or web-component approaches.

**Shell / Host pattern**: the shell-app owns routing, auth context (`AuthContext`), and the layout shell. It loads the Orders MFE at runtime via a dynamic `import("ordersMfe/OrdersApp")`. The shell exposes `token` and `user` through React Context so remote MFEs can consume auth state without re-implementing login logic.

**SPA routing inside each MFE**: React Router v6 is used inside the Orders MFE with nested `<Routes>`. The shell passes `/*` to the remote, so the MFE controls its own sub-routes (`/orders`, `/orders/new`, `/orders/:id`).

**API layer separation**: each MFE owns its own `services/` folder with typed API calls. The gateway URL (`http://localhost:8080`) is the single entry point — MFEs never call microservice ports directly.

### Infrastructure

**Nginx as API gateway** provides path-based routing (`/api/orders/*` → orders-service, `/api/users/*` → users-service) and serves as the single public port (8080) for the entire platform. In a cloud deployment this would be replaced by an AWS ALB, GCP Cloud Load Balancer, or a dedicated API gateway like Kong.

**Docker Compose healthchecks** ensure the database containers are accepting connections before the application services start, preventing race-condition startup failures.

---

## What would change with more time

### Security
- JWT verification middleware in every downstream service (currently only the users-service issues tokens)
- HTTPS / TLS termination at the gateway
- Refresh token rotation with Redis-backed revocation list
- Rate limiting at the gateway layer (Nginx `limit_req` or a dedicated rate limiter)
- Role-based access control (RBAC) enforced per endpoint based on the JWT `role` claim

### Observability
- Structured JSON logging with correlation IDs propagated across services via `X-Request-ID` headers
- Distributed tracing with OpenTelemetry (exporters: Jaeger or Tempo)
- Prometheus metrics endpoint on each service (`/metrics`), scraped by Prometheus, visualised in Grafana
- Alerting rules for error rate, P99 latency, and queue depth

### Data & persistence
- Alembic migrations fully activated with a migration runner container in Docker Compose
- Read replicas for PostgreSQL to separate read and write workloads
- Redis usage formalized: session store, distributed lock for order state transitions, caching layer for catalog data
- MongoDB for unstructured order event log (append-only event sourcing pattern)

### Architecture
- Asynchronous order events via a message broker (RabbitMQ or Kafka): order creation publishes an event, a notification service consumes it to send confirmation emails
- Catalog service extracted from optional to required: its own FastAPI service with a MongoDB or Redis backend
- API Gateway upgraded to Kong or AWS API Gateway for plugin-based auth, rate limiting, and analytics
- Kubernetes manifests (Helm charts) replacing Docker Compose for production deployment

### Frontend
- Micro-frontend contract testing (Pact or similar) to verify the shell-MFE integration at CI time
- Design system / shared component library extracted to its own npm package consumed by all MFEs
- End-to-end tests with Playwright covering the full login → create order → update status flow
- Error boundary components wrapping each remote MFE to prevent a failing remote from crashing the shell
- Dynamic remote URL configuration via environment variables at container runtime (currently hardcoded to localhost)

### Testing
- Integration tests with a real PostgreSQL test instance (using pytest-postgresql or Testcontainers)
- Contract tests between services
- Load tests with Locust to validate throughput before production
- Mutation testing to measure test suite effectiveness
