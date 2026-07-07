# Data Space frontend (standalone)

A standalone Django project that renders the new "Data Space" dashboard section
using the real EnergyGuard-frontend theme (Phoenix Bootstrap 5 admin theme,
Nunito Sans, the same `theme.min.css`/`user.min.css`, the same sidebar/header/
footer markup patterns) - built to run entirely on its own for now, and be
easy to fold into the real `EnergyGuard-frontend` Django project later.

## How it's wired

- **No Django auth, no database, no Keycloak.** This project has no models,
  no migrations, and doesn't use `django.contrib.auth`/`sessions`/`admin`.
  Authentication is entirely client-side: the browser logs in directly against
  the [EnergyGuard Data Space FastAPI gateway](../README.md)'s `/auth/login`,
  holds the token in `sessionStorage`, and attaches it to every subsequent
  call. Django's only job here is serving the themed page shell and static
  assets.
- All data (offerings, subscriptions, consumed files, etc.) is fetched
  **directly from the browser** to the gateway (`static/dataspace/js/api.js`)
  - CORS is already enabled on the gateway, so no server-side proxy is needed.

## Running standalone

Uses the same virtualenv as the gateway (`../energyguard-dataspace-venv`) -
no separate venv for this project.

```bash
cd ..   # project root
source energyguard-dataspace-venv/bin/activate
pip install -r dataspace-frontend/requirements.txt

# Point at your running FastAPI gateway (see ../README.md to start it - default port 8000)
export DATASPACE_GATEWAY_URL=http://localhost:8000

cd dataspace-frontend
python manage.py runserver 8081
```

Open http://localhost:8081/ - log in with your Middleware/EnerTEF credentials
(the same ones used against the gateway directly).

Note: the gateway's `DATASPACE_CORS_ALLOWED_ORIGINS` must include
`http://localhost:8081` (or be `*`) for the browser calls to succeed - see
the gateway's own `.env`.

## What's copied from the real theme vs. original

**Copied verbatim** from `../dashboard/EnergyGuard-frontend/`:
- `dataspace/static/assets/css/theme.min.css`, `user.min.css`
- `dataspace/static/assets/js/phoenix.js`, `config.js`
- `dataspace/static/vendors/{popper,bootstrap,anchorjs,is,fontawesome,lodash,feather-icons,dayjs,simplebar}`
- Logo images actually referenced by the header/favicon
- `dataspace/templates/core/footer.html`

**Adapted copies** (same structure/classes, so a future merge is a small diff,
not a rewrite):
- `dataspace/templates/core/authenticated-base.html` - dropped the
  notification-polling and Django-messages JS blocks, which reference URL
  names (`poll_notifications`, `read_notification`, ...) that only exist in
  the real app's `core` Django app.
- `dataspace/templates/core/vertical-navbar.html` - same `<li>` structure and
  classes as the real sidebar, but items other than "Data Space" point to
  `href="#"` with a `standalone-disabled` class (they're not real pages in
  this standalone project). When merging: swap those back to their real
  `{% url %}` names and insert the new "Data Space" `<li>` into the real file.
- `dataspace/templates/core/header.html` - kept the logo/theme-toggle, but
  replaced the Django-auth-dependent notifications/avatar dropdowns with a
  simple login/logout widget driven by `app.js`.

**New** (this feature's own code, not from the theme):
- `dataspace/templates/dataspace/index.html` - the actual page: stat cards,
  tabs (My Data / My Subscriptions / Browse Catalog / My Offerings / Incoming
  Requests), tables, and two modals (Create Offering, Upload Data) - all built
  from the same Bootstrap/Phoenix markup patterns used elsewhere in the real
  app (e.g. `datasets/templates/datasets/datasets-list.html`'s tab/filter-pill/
  table pattern, `core/templates/core/dashboard.html`'s stat-card pattern).
- `dataspace/static/dataspace/js/api.js` - thin fetch wrapper for the gateway.
- `dataspace/static/dataspace/js/app.js` - all the page's interactive logic.

## Merging into the real EnergyGuard-frontend later

1. Copy the `dataspace/` Django app folder into the main project.
2. Add `path("data-space/", include("dataspace.urls"))` to `main/urls.py`.
3. Add `"dataspace"` to `INSTALLED_APPS`.
4. In the real `vertical-navbar.html`, insert this project's "Data Space"
   `<li>` (see `authenticated-base.html` comment above for the exact spot).
5. Delete `dataspace/templates/core/*` and `dataspace/static/assets/`,
   `dataspace/static/vendors/` from this project's app folder - the real
   project already provides those via its own `core` app and shared static
   root; only `dataspace/templates/dataspace/index.html` and
   `dataspace/static/dataspace/js/*.js` need to actually move over.
6. Set `DATASPACE_GATEWAY_URL` in the real project's settings/env.
