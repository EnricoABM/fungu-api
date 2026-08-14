# Fungu API Routes

Complete reference for all 15 REST endpoints exposed by the Fungu API.

Base URL: `http://127.0.0.1:8000`

Interactive Swagger docs are available at `/docs` once the server is running.

---

## Table of Contents

- [Authentication Flow](#authentication-flow)
- [Data Models](#data-models)
- [Endpoints](#endpoints)
  - [1. POST /users/register](#1-post-usersregister)
  - [2. POST /auth/login](#2-post-authlogin)
  - [3. POST /auth/login-form](#3-post-authlogin-form)
  - [4. GET /auth/refresh](#4-get-authrefresh)
  - [5. POST /device/master/register](#5-post-devicemasterregister)
  - [6. POST /device/register](#6-post-deviceregister)
  - [7. POST /alerts/register](#7-post-alertsregister)
  - [8. PATCH /users/contacts](#8-patch-userscontacts)
  - [9. GET /measurements](#9-get-measurements)
  - [10. GET /measurements/latest](#10-get-measurementslatest)
  - [11. GET /device/masters](#11-get-devicemasters)
  - [12. GET /device/masters/{mac}/slaves](#12-get-devicemastersmacslaves)
  - [13. GET /device/slaves](#13-get-deviceslaves)
  - [14. GET /users/me](#14-get-usersme)
  - [15. GET /alerts](#15-get-alerts)

---

## Authentication Flow

The API uses JWT-based authentication with two token types: an **access token** and a **refresh token**. Both are issued on login.

### Step-by-step

1. **Register** a new account via `POST /users/register`. No authentication needed.
2. **Login** via `POST /auth/login` (JSON body) or `POST /auth/login-form` (OAuth2 form). You receive both tokens.
3. **Store** the `access_token` and `refresh_token` on the client side.
4. **Send** the access token in the `Authorization` header as a Bearer token for all protected routes:
   ```
   Authorization: Bearer <access_token>
   ```
5. **Refresh** when the access token expires. Call `GET /auth/refresh?token=<refresh_token>` to get a new access token. The refresh token goes in a query parameter, not the header.
6. **Token expiry** is configurable through environment variables `ACCESS_TOKEN_EXPIRE_MINUTES` and `REFRESH_TOKEN_EXPIRE_MINUTES`. Both values are in minutes.

### Token structure

Both tokens are JWTs signed with the configured `SECRET_KEY` and `ALGORITHM`. The payload contains:

| Field | Description |
|-------|-------------|
| `sub` | User ID (as string) |
| `exp` | Expiration timestamp |
| `typ` | Token type: `"access"` or `"refresh"` |

The refresh endpoint validates that `typ` equals `"refresh"` before issuing a new access token.

### Auth requirements by endpoint

| Auth level | Endpoints |
|------------|-----------|
| None | `POST /users/register`, `POST /auth/login`, `POST /auth/login-form`, `POST /device/master/register`, `POST /device/register` |
| Bearer Token | All `/measurements`, `/alerts`, `/device/masters`, `/device/slaves`, `/users/me`, `/users/contacts` |
| Query Parameter (refresh token) | `GET /auth/refresh` |

---

## Data Models

Five SQLAlchemy models back the API. Below is a field-level description of each.

### User

Table: `user_tb`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | int | PK, autoincrement | Unique user identifier |
| `email` | str | unique, not null | Login email |
| `password_hash` | str | not null | Bcrypt-hashed password |
| `telegram_chat_id` | str | nullable | Telegram chat ID for alert notifications |
| `alert_email` | str | nullable | Email address for alert notifications |

### Master

Table: `master_tb`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `mac` | str | PK | MAC address of the master device |

### Slave

Table: `slave_tb`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `mac` | str | PK | MAC address of the slave device |
| `master` | str | FK to `master_tb.mac`, nullable | MAC address of the parent master device |

### Measurement

Table: `measurement_tb`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | int | PK, autoincrement | Unique measurement identifier |
| `measured_at` | datetime | not null | Timestamp of the measurement |
| `variable` | str | not null | Variable name (e.g. temperature, humidity) |
| `value` | str | not null | Measured value, stored as string |

> **EAV pattern note:** Measurements use an Entity-Attribute-Value design. Each row stores a single variable name and its corresponding value rather than having one column per sensor reading. The `value` column is a `String` in the database, but the API response schemas cast it to `float` before returning.

> **Variable name inconsistency:** Variable names differ between data sources. The MQTT payload uses Portuguese names (`temperatura`, `umidade`, `luminosidade`), while the `MeasurementRegister` schema uses English abbreviations (`temp`, `hum`, `lux`). When querying measurements by variable, check both naming conventions. The variable names stored in the database depend on which source wrote the record.

### AlertConfig

Table: `alert_config_tb`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | int | PK, autoincrement | Unique alert identifier |
| `user_id` | int | FK to `user_tb.id`, not null | Owner of this alert configuration |
| `variable` | str | not null | Variable to monitor (e.g. `temperatura`) |
| `condition` | str | not null | Comparison operator: `>`, `<`, or `==` |
| `threshold` | float | not null | Value to compare against |

---

## Endpoints

---

### 1. POST /users/register

Register a new user account.

**Authentication:** None

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | yes | User email address |
| `password` | string | yes | Plaintext password (hashed with bcrypt before storage) |

**Success response:** `200 OK`

```json
{
  "mensagem": "cadastrado com sucesso"
}
```

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 400 | `"E-mail inválido"` | Email already registered |

**curl:**

```bash
curl -X POST http://127.0.0.1:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123"}'
```

---

### 2. POST /auth/login

Authenticate with email and password. Returns both access and refresh tokens.

**Authentication:** None

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | yes | Registered email |
| `password` | string | yes | Account password |

**Success response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "Bearer"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | JWT access token for Bearer auth |
| `refresh_token` | string | JWT refresh token for token renewal |
| `token_type` | string | Always `"Bearer"` |

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 400 | `"Credenciais Inválidas"` | Wrong email or password |

**curl:**

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123"}'
```

---

### 3. POST /auth/login-form

OAuth2-compatible login using form-encoded credentials. Returns the same token pair as `POST /auth/login`.

**Authentication:** None

**Request body:** `application/x-www-form-urlencoded`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | yes | Registered email (mapped to email internally) |
| `password` | string | yes | Account password |

**Success response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "Bearer"
}
```

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 400 | `"Credenciais Inválidas"` | Wrong email or password |

**curl:**

```bash
curl -X POST http://127.0.0.1:8000/auth/login-form \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secret123"
```

---

### 4. GET /auth/refresh

Exchange a refresh token for a new access token. The refresh token is passed as a query parameter, not in the Authorization header.

**Authentication:** Refresh token (query parameter)

**Query parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `token` | string | yes | Refresh token obtained from login |

**Success response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "Bearer"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | New JWT access token |
| `token_type` | string | Always `"Bearer"` |

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 401 | `"Token Inválido"` | Invalid, expired, or wrong token type |
| 401 | `"Acesso Negado"` | User no longer exists |

**curl:**

```bash
curl -X GET "http://127.0.0.1:8000/auth/refresh?token=eyJhbGciOi..."
```

---

### 5. POST /device/master/register

Register a master device by its MAC address.

**Authentication:** None

**Request body:**

```json
{
  "mac": "AA:BB:CC:DD:EE:FF"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mac` | string | yes | MAC address of the master device |

**Success response:** `200 OK`

No response body (empty 200).

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 400 | `"Mestre já cadastrado"` | Master with this MAC already registered |

**curl:**

```bash
curl -X POST http://127.0.0.1:8000/device/master/register \
  -H "Content-Type: application/json" \
  -d '{"mac": "AA:BB:CC:DD:EE:FF"}'
```

---

### 6. POST /device/register

Register a slave device linked to an existing master device.

**Authentication:** None

**Request body:**

```json
{
  "mac_master": "AA:BB:CC:DD:EE:FF",
  "mac_slave": "11:22:33:44:55:66"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mac_master` | string | yes | MAC address of the parent master device |
| `mac_slave` | string | yes | MAC address of the slave device to register |

**Success response:** `200 OK`

No response body (empty 200).

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 400 | `"Dispositivo já cadastrado"` | Slave with this MAC already registered |
| 400 | `"Mestre não cadastrado"` | Referenced master MAC does not exist |

**curl:**

```bash
curl -X POST http://127.0.0.1:8000/device/register \
  -H "Content-Type: application/json" \
  -d '{"mac_master": "AA:BB:CC:DD:EE:FF", "mac_slave": "11:22:33:44:55:66"}'
```

---

### 7. POST /alerts/register

Create an alert configuration for the authenticated user. The alert monitors a variable and triggers when the condition is met.

**Authentication:** Bearer Token

**Request body:**

```json
{
  "variable": "temperatura",
  "condition": ">",
  "threshold": 30.0
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `variable` | string | yes | Variable name to monitor |
| `condition` | string | yes | Comparison operator: `>`, `<`, or `==` |
| `threshold` | float | yes | Threshold value to compare against |

**Success response:** `200 OK`

```json
{
  "mensagem": "Alerta configurado."
}
```

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 401 | `"Token Inválido"` | Missing or invalid access token |
| 401 | `"Acesso Negado"` | User not found |

**curl:**

```bash
curl -X POST http://127.0.0.1:8000/alerts/register \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"variable": "temperatura", "condition": ">", "threshold": 30.0}'
```

---

### 8. PATCH /users/contacts

Update the notification contacts (Telegram chat ID and/or alert email) for the authenticated user. Only provided fields are updated; omitted fields remain unchanged.

**Authentication:** Bearer Token

**Request body:**

```json
{
  "telegram_chat_id": "123456789",
  "alert_email": "alerts@example.com"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `telegram_chat_id` | string | no | Telegram chat ID for notifications |
| `alert_email` | string | no | Email address for alert notifications |

**Success response:** `200 OK`

```json
{
  "mensagem": "Contatos atualizados com sucesso."
}
```

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 401 | `"Token Inválido"` | Missing or invalid access token |
| 401 | `"Acesso Negado"` | User not found |
| 404 | `"Usuário não encontrado"` | User not found in database |

**curl:**

```bash
curl -X PATCH http://127.0.0.1:8000/users/contacts \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"telegram_chat_id": "123456789", "alert_email": "alerts@example.com"}'
```

---

### 9. GET /measurements

Retrieve a paginated, filterable list of measurements. Supports filtering by variable name and date range.

**Authentication:** Bearer Token

**Query parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `variable` | string | no | null | Filter by variable name |
| `start_date` | datetime | no | null | Filter measurements from this date (ISO 8601) |
| `end_date` | datetime | no | null | Filter measurements up to this date (ISO 8601) |
| `page` | int | no | 1 | Page number (1-based) |
| `page_size` | int | no | 50 | Number of records per page |

**Success response:** `200 OK`

```json
{
  "measurements": [
    {
      "id": 1,
      "measured_at": "2025-08-14T12:00:00",
      "variable": "temperatura",
      "value": 25.4
    },
    {
      "id": 2,
      "measured_at": "2025-08-14T12:00:00",
      "variable": "umidade",
      "value": 63.2
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 50
}
```

| Field | Type | Description |
|-------|------|-------------|
| `measurements` | array | List of measurement objects |
| `measurements[].id` | int | Measurement ID |
| `measurements[].measured_at` | datetime | Timestamp of measurement |
| `measurements[].variable` | string | Variable name |
| `measurements[].value` | float | Measured value (cast from string) |
| `total` | int | Total number of matching records |
| `page` | int | Current page number |
| `page_size` | int | Page size used for this query |

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 401 | `"Token Inválido"` | Missing or invalid access token |
| 401 | `"Acesso Negado"` | User not found |
| 400 | (varies) | Invalid filter parameters |

**curl:**

```bash
curl -X GET "http://127.0.0.1:8000/measurements?variable=temperatura&start_date=2025-08-01T00:00:00&end_date=2025-08-14T23:59:59&page=1&page_size=50" \
  -H "Authorization: Bearer <access_token>"
```

---

### 10. GET /measurements/latest

Retrieve the most recent measurement for each variable. Returns one entry per variable.

**Authentication:** Bearer Token

**Query parameters:** None

**Success response:** `200 OK`

```json
[
  {
    "variable": "temperatura",
    "value": 25.4,
    "measured_at": "2025-08-14T12:00:00"
  },
  {
    "variable": "umidade",
    "value": 63.2,
    "measured_at": "2025-08-14T12:00:00"
  },
  {
    "variable": "luminosidade",
    "value": 450.0,
    "measured_at": "2025-08-14T12:00:00"
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `variable` | string | Variable name |
| `value` | float | Latest measured value (cast from string) |
| `measured_at` | datetime | Timestamp of the measurement |

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 401 | `"Token Inválido"` | Missing or invalid access token |
| 401 | `"Acesso Negado"` | User not found |
| 400 | (varies) | Internal query error |

**curl:**

```bash
curl -X GET http://127.0.0.1:8000/measurements/latest \
  -H "Authorization: Bearer <access_token>"
```

---

### 11. GET /device/masters

List all registered master devices.

**Authentication:** Bearer Token

**Query parameters:** None

**Success response:** `200 OK`

```json
[
  {
    "mac": "AA:BB:CC:DD:EE:FF"
  },
  {
    "mac": "11:22:33:44:55:66"
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `mac` | string | MAC address of the master device |

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 401 | `"Token Inválido"` | Missing or invalid access token |
| 401 | `"Acesso Negado"` | User not found |

**curl:**

```bash
curl -X GET http://127.0.0.1:8000/device/masters \
  -H "Authorization: Bearer <access_token>"
```

---

### 12. GET /device/masters/{mac}/slaves

List all slave devices registered under a specific master device.

**Authentication:** Bearer Token

**Path parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mac` | string | yes | MAC address of the master device |

**Success response:** `200 OK`

```json
[
  {
    "mac": "11:22:33:44:55:66",
    "master": "AA:BB:CC:DD:EE:FF"
  },
  {
    "mac": "77:88:99:AA:BB:CC",
    "master": "AA:BB:CC:DD:EE:FF"
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `mac` | string | MAC address of the slave device |
| `master` | string | MAC address of the parent master device |

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 401 | `"Token Inválido"` | Missing or invalid access token |
| 401 | `"Acesso Negado"` | User not found |

**curl:**

```bash
curl -X GET http://127.0.0.1:8000/device/masters/AA:BB:CC:DD:EE:FF/slaves \
  -H "Authorization: Bearer <access_token>"
```

---

### 13. GET /device/slaves

List all registered slave devices across all masters.

**Authentication:** Bearer Token

**Query parameters:** None

**Success response:** `200 OK`

```json
[
  {
    "mac": "11:22:33:44:55:66",
    "master": "AA:BB:CC:DD:EE:FF"
  },
  {
    "mac": "77:88:99:AA:BB:CC",
    "master": "11:22:33:44:55:66"
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `mac` | string | MAC address of the slave device |
| `master` | string | MAC address of the parent master device |

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 401 | `"Token Inválido"` | Missing or invalid access token |
| 401 | `"Acesso Negado"` | User not found |

**curl:**

```bash
curl -X GET http://127.0.0.1:8000/device/slaves \
  -H "Authorization: Bearer <access_token>"
```

---

### 14. GET /users/me

Retrieve the profile of the currently authenticated user.

**Authentication:** Bearer Token

**Query parameters:** None

**Success response:** `200 OK`

```json
{
  "id": 1,
  "email": "user@example.com",
  "telegram_chat_id": "123456789",
  "alert_email": "alerts@example.com"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | User ID |
| `email` | string | User email address |
| `telegram_chat_id` | string or null | Telegram chat ID, if set |
| `alert_email` | string or null | Alert email, if set |

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 401 | `"Token Inválido"` | Missing or invalid access token |
| 401 | `"Acesso Negado"` | User not found |
| 404 | `"Usuário não encontrado"` | User not found in database |

**curl:**

```bash
curl -X GET http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer <access_token>"
```

---

### 15. GET /alerts

List all alert configurations belonging to the authenticated user.

**Authentication:** Bearer Token

**Query parameters:** None

**Success response:** `200 OK`

```json
{
  "alerts": [
    {
      "id": 1,
      "variable": "temperatura",
      "condition": ">",
      "threshold": 30.0
    },
    {
      "id": 2,
      "variable": "umidade",
      "condition": "<",
      "threshold": 40.0
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `alerts` | array | List of alert configurations |
| `alerts[].id` | int | Alert ID |
| `alerts[].variable` | string | Monitored variable name |
| `alerts[].condition` | string | Comparison operator: `>`, `<`, or `==` |
| `alerts[].threshold` | float | Threshold value |

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| 401 | `"Token Inválido"` | Missing or invalid access token |
| 401 | `"Acesso Negado"` | User not found |

**curl:**

```bash
curl -X GET http://127.0.0.1:8000/alerts \
  -H "Authorization: Bearer <access_token>"
```

---

## Endpoint Summary

| # | Method | Path | Auth |
|---|--------|------|------|
| 1 | POST | `/users/register` | None |
| 2 | POST | `/auth/login` | None |
| 3 | POST | `/auth/login-form` | None |
| 4 | GET | `/auth/refresh` | Refresh token (query param) |
| 5 | POST | `/device/master/register` | None |
| 6 | POST | `/device/register` | None |
| 7 | POST | `/alerts/register` | Bearer Token |
| 8 | PATCH | `/users/contacts` | Bearer Token |
| 9 | GET | `/measurements` | Bearer Token |
| 10 | GET | `/measurements/latest` | Bearer Token |
| 11 | GET | `/device/masters` | Bearer Token |
| 12 | GET | `/device/masters/{mac}/slaves` | Bearer Token |
| 13 | GET | `/device/slaves` | Bearer Token |
| 14 | GET | `/users/me` | Bearer Token |
| 15 | GET | `/alerts` | Bearer Token |