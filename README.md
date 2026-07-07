# EnergyGuard Data Space Gateway

A FastAPI gateway over the EnPower / True Connector Data Space APIs. It exposes a
clean REST interface (with automatic Swagger/OpenAPI docs) for the full **Data
Provide** and **Data Consume** workflows: authentication, Data Offering management,
subscription requests, and provide/consume of data files.

The gateway is a thin, stateless proxy: it does not store credentials or tokens. You
authenticate once via `POST /auth/login` to obtain an access token from the upstream
Middleware, then pass that same token as `Authorization: Bearer <token>` on every
other call to this gateway, which forwards it upstream unchanged.

## Requirements

- Python 3.10+
- A Middleware account (username/password) on the target Data Space instance

## Setup

```bash
python3 -m venv energyguard-dataspace-venv
source energyguard-dataspace-venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and adjust if your deployment uses different base
URLs (e.g. a different True Connector local API host):

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `DATASPACE_ENPOWER_BASE_URL` | `https://enpower.eurodyn.com` | Base URL of the EnPower Middleware API |
| `DATASPACE_CONNECTOR_BASE_URL` | `https://true-connector-1-server-localapi.eurodyn.com` | Base URL of your True Connector local API (set in your Connector Configuration) |
| `DATASPACE_REQUEST_TIMEOUT` | `30` | Upstream request timeout, in seconds |

Running against your own connector deployment (rather than the sample
`enpower.eurodyn.com` / `true-connector-1-server-localapi.eurodyn.com` hosts from
the docs) only requires changing these two URLs. See
[CONNECTOR_CONFIG.md](CONNECTOR_CONFIG.md) for how they map to your True
Connector stack's own `.env`, and which of *that* stack's variables you must
customize per deployment vs. which are safe to leave as shared defaults.

## Running

```bash
uvicorn dataspace_gateway.main:app --reload --port 8000
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI schema: http://localhost:8000/openapi.json
- Health check: http://localhost:8000/health

## Testing

```bash
pip install -r requirements-dev.txt
pytest -v -s
```

The suite in `tests/` calls the FastAPI app in-process (no separately running
server needed) using the credentials in `DATASPACE_TEST_USERNAME` /
`DATASPACE_TEST_PASSWORD` from `.env`, and exercises the real dataspace:

- All read endpoints (`/offerings/*`, `/subscriptions/*`, `/data/consumed`) hit
  the live Middleware and assert a 200 + list response.
- `test_provide_data` performs a real (non-mocked) upload of a harmless
  `test.txt` file to a Data Offering you own — it skips cleanly instead of
  failing if your account doesn't own one yet.
- Nothing else with side effects (`POST /offerings`, `POST /subscriptions`,
  responding to requests) is covered, since running those against a shared
  production dataspace would create real, visible clutter on every test run.

Alternatively, `scripts/smoke_test.sh` does a quicker curl-based version of the
same read-only checks against an already-running gateway.

## Authentication

Every endpoint except `/auth/login` requires an `Authorization: Bearer <token>`
header. Get a token first:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "enpower-user", "password": "XXX"}'
```

Response:

```json
{
  "accessToken": "eyJhbGciOi...",
  "user": { "id": "...", "username": "Enpower-user1", "email": "enpower-user1@eurodyn.com" }
}
```

Use `accessToken` as the bearer token on all subsequent calls in this guide.

**In Swagger UI (`/docs`)**: click the padlock/"Authorize" button at the top of
the page once, paste the token (without the word "Bearer"), and it's applied
automatically to every endpoint's "Try it out" — no need to paste it again per
route.

## Endpoint reference

All endpoints below are on **this gateway** (default `http://localhost:8000`), not
on the upstream Data Space directly. The gateway forwards each call to the
corresponding upstream endpoint (shown in parentheses).

### Data Offerings

| Method | Path | Upstream call | Description |
|---|---|---|---|
| POST | `/offerings` | `POST /api/dataset/v2/my_offered_services` | Create a new Data Offering |
| GET | `/offerings/mine` | `GET /api/datalist/my_offered_services` | List Data Offerings you own |
| GET | `/offerings/catalog` | `GET /api/datalist/cross_platform_service` | List available Category/Sub-Category/Business Object types |
| GET | `/offerings/available` | `GET /api/datalist/my_catalog` | Discover Data Offerings published by other participants |

Create a Data Offering:

```bash
curl -X POST http://localhost:8000/offerings \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "ED example 17/4",
    "data_catalog_business_object_id": "ea86b95d-4419-4baf-bcf1-9d99acd80e89",
    "profile_selector": "json",
    "active_from": "2026-04-01T14:26:00.407968Z",
    "active_to": "2026-04-04T14:26:00.408686Z",
    "updating_frequency": "60"
  }'
```

`data_catalog_business_object_id` comes from `GET /offerings/catalog`. Response:

```json
{ "response": "794975e9-7432-4350-b32e-0550019f6e40" }
```

### Subscriptions

| Method | Path | Upstream call | Description |
|---|---|---|---|
| GET | `/subscriptions/mine` | `GET /api/datalist/my_subscriptions` | List Data Offerings you're subscribed to |
| POST | `/subscriptions` | `POST /api/dataset/v2/new_subscription` | Request a subscription to another participant's Data Offering |
| GET | `/subscriptions/requests` | `GET /api/datalist/requests_on_offered_services` | List subscription requests received on your own Data Offerings |
| POST | `/subscriptions/requests/{request_id}/respond` | `POST /api/dataset/v2/requests_on_offered_services?id=...` | Accept or reject a pending request |

Subscribe to a Data Offering discovered via `GET /offerings/available`:

```bash
curl -X POST http://localhost:8000/subscriptions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"data_catalog_data_offering_id": "8de267c7-0c72-432b-89ce-8a5759a32978"}'
```

Accept a pending request (`request_id` is the `request_id` from
`GET /subscriptions/requests`):

```bash
curl -X POST http://localhost:8000/subscriptions/requests/9340034c-f8bf-40c0-98ea-e5023cd10446/respond \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "accept"}'
```

Any extra fields from the request row (as returned by `GET /subscriptions/requests`)
may be included in the body alongside `status` — they are forwarded upstream as-is.

### Data Provide / Consume

| Method | Path | Upstream call | Description |
|---|---|---|---|
| POST | `/data/provide` | `POST /api/provide-data` (True Connector local API) | Upload a Data Entity for a Data Offering |
| GET | `/data/consumed` | `GET /api/datalist/data_consumed` | List Data Entities published under your subscriptions |
| GET | `/data/consumed/{entity_id}` | `GET /api/consume-data/by-id?id=...` (True Connector local API) | Download a Data Entity's file content |

Provide data for a Data Offering you own:

```bash
curl -X POST http://localhost:8000/data/provide \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "ed",
    "description": "ed descr",
    "filename": "Hello.txt",
    "file": "Hello",
    "data_offering_id": "d34de515-54ef-4038-8354-7d9407816405"
  }'
```

Consume (download) a Data Entity by ID. The connector's own API wraps the file
as a base64 data URI inside JSON (`{"filedata": "data:<mime>;base64,...", ...}`)
- this endpoint decodes that for you and returns the real file bytes with the
correct content type. Pass `filename` (from `GET /data/consumed`) to also get a
proper `Content-Disposition` header:

```bash
curl "http://localhost:8000/data/consumed/a6a3ca0f-49b6-4d87-a3fc-3c3490b99258?filename=data.csv" \
  -H "Authorization: Bearer <token>" \
  -o downloaded_file.csv
```

## End-to-end workflows

### Provide data

1. `POST /auth/login` — get an access token.
2. `GET /offerings/catalog` — find the Business Object ID for the service you want to offer.
3. `POST /offerings` — create the Data Offering, get its ID back.
4. `GET /subscriptions/requests` — periodically check for incoming subscription requests on your offering.
5. `POST /subscriptions/requests/{request_id}/respond` — accept (or reject) a request.
6. `POST /data/provide` — upload the data file against your `data_offering_id`.

### Consume data

1. `POST /auth/login` — get an access token.
2. `GET /offerings/available` — discover Data Offerings from other participants and pick a `cf_id`.
3. `POST /subscriptions` — request a subscription using that `data_catalog_data_offering_id`.
4. Wait for the provider to accept your request.
5. `GET /data/consumed` — list Data Entities available under your accepted subscriptions.
6. `GET /data/consumed/{entity_id}` — download the file.

## Error handling

Upstream error responses (status >= 400) are passed through with the same HTTP
status code, and the response body under `detail` is either the upstream JSON error
or its raw text if it wasn't JSON. A `502` means the gateway couldn't reach the
upstream host at all (network/timeout error).

Authentication failures use a structured `detail.error_code` instead of a plain
string, so a frontend can reliably branch on them instead of guessing from message
text:

| `error_code` | Meaning |
|---|---|
| `token_expired` | The access token's own `exp` claim is in the past - detected locally, no upstream call made |
| `invalid_token` | Upstream itself rejected the token (bad signature, revoked, malformed) - the original upstream error is included under `upstream_detail` |
| `missing_token` | (download endpoint only) Neither an `Authorization` header nor a `?token=` query parameter was provided |

## Frontend-friendly response shapes

- `GET /offerings/mine`, `GET /offerings/available`, and `GET /subscriptions/requests`
  add `category_path` (a clean `list[str]` breadcrumb) and, where applicable,
  `subscribers` (a clean `list[{status, company, username}]`) alongside the raw
  `category` / `subscriptions` fields upstream returns as HTML strings. Prefer the
  parsed fields; the raw ones are kept only for backwards compatibility.
- `GET /data/consumed/{entity_id}` accepts the access token either as the normal
  `Authorization` header or as a `?token=` query parameter - the latter lets a plain
  `<a href="...">` trigger a download directly in a browser without JavaScript
  needing to attach a custom header. This is the only endpoint that accepts a
  query-param token; everywhere else still requires the header.

## Project layout

```
dataspace_gateway/
  main.py              FastAPI app, router wiring, /health
  config.py            Settings (base URLs, timeout) via environment variables
  dependencies.py      Bearer token extraction/validation
  upstream_client.py   Shared httpx client wrapper for calling upstream services
  formatting.py        Cleans up HTML-embedded upstream fields into structured JSON
  schemas.py           Pydantic request/response models
  routers/
    auth.py            POST /auth/login
    offerings.py       /offerings/*
    subscriptions.py   /subscriptions/*
    data.py            /data/*
```
