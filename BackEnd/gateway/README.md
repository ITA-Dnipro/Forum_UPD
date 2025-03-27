# Authorization Service with Krakend Gateway

This service provides JWT-based authorization and permission checking for users with different roles, integrated with Krakend Gateway. It uses PostgreSQL and Go for persistence and includes automatic role and permission seeding.

---

##  Functionality Overview

### ✅ Features
- JWT token validation (`/check`)
- Role-based permission checking (`/permissions/check`)
- Auto-migration and seeding of roles/permissions
- Dockerized setup
- Swagger API documentation

---

## 🚀 Endpoints

### `GET /check`
- **Description**: Validates JWT token and checks if user has the required role (optional).
- **Headers**: `Authorization: Bearer <token>`
- **Query param (optional)**: `requiredRole` – e.g., `IsStartup`, `IsInvestor`
- **Response**:
  - `200 OK` → valid token (and matching role, if provided)
  - `401 Unauthorized` → missing/invalid/expired token
  - `403 Forbidden` → role doesn't match required role

### `GET /permissions/check`
- **Description**: Checks if the authenticated user has `IsStartup` or `IsInvestor` role.
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  - `200 OK` → JSON object with roles and user ID
  - `401` / `403` / `404` depending on auth/role errors

### Swagger Docs
- URL: `http://localhost:8080/swagger/index.html`

---

## ️ Technologies

- Go (Golang)
- GORM (PostgreSQL ORM)
- JWT (`github.com/golang-jwt/jwt/v4`)
- Krakend Gateway
- Docker + Docker Compose

---

##  Environment Variables

Add these variables to `.env` or `simple.env` file:

```env
DB_USER=db_user
DB_PASSWORD=db_password
DB_HOST=db_host
DB_PORT=db_port
DB_NAME=db_name

```

## Database Migrations

Database tables and seed data (roles, permissions, role-permission mappings) are created automatically on startup via AutoMigrate() and SeedOrUpdateDB().

You do not need to run any manual migrations.

## Build and Run
```env
docker-compose -f docker-compose.gateway.dev.yml up --build
```
- Auth service: http://localhost:8080
- Krakend gateway: http://localhost:8081```
