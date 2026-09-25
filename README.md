# ORIK Webcraft API

Django REST Framework service behind the ORIK Webcraft site. It serves the
site's editable copy and receives contact-form enquiries. The admin is themed
with Jazzmin.

## Run it

```bash
cd backend
python -m venv .venv                 # first time only
./.venv/Scripts/python.exe -m pip install -r requirements.txt
cp .env.example .env                 # then fill it in
./.venv/Scripts/python.exe manage.py migrate
./.venv/Scripts/python.exe manage.py seed_content   # loads the site's current copy
./.venv/Scripts/python.exe manage.py createsuperuser
./.venv/Scripts/python.exe manage.py runserver 8001
```

Port 8000 is often taken by another project on this machine, so the frontend is
configured for **8001**. On macOS/Linux use `.venv/bin/python` instead.

The frontend reads the API origin from `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8001
```

That value is inlined at build time, so **restart `next dev` after changing it**.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/enquiries/` | Submit a contact-form enquiry. Returns `201` with the created record. |
| `GET` | `/api/content/` | All site copy in one payload. This is what the frontend reads. |
| `GET` | `/api/content/<section>/` | One section on its own, e.g. `faqs`, `packages`, `process-steps`. Read-only. |
| `GET` | `/api/health/` | Liveness probe. |
| — | `/admin/` | Edit content and triage enquiries. |

### `POST /api/enquiries/`

```json
{
  "name": "Aarati Shrestha",
  "business": "Himalayan Treks",
  "email": "aarati@himalayantreks.test",
  "phone": "+977 9812345678",
  "package": "Growth",
  "message": "We need a booking enquiry form and a gallery."
}
```

`name`, `business`, `email` and `phone` are required; `package` and `message`
are optional. Responses: `201` created, `400` validation error (field-keyed),
`429` rate limited.

## How it's protected

The endpoint is public by necessity, so it leans on three cheap defences:

- **Honeypot.** The form renders a hidden `website` input. People never see it;
  bots that fill every field get a `400`. The error text is deliberately vague
  so a bot can't learn which field caught it.
- **Rate limit.** 5 submissions per IP per hour (`ENQUIRY_RATE_LIMIT`). Behind a
  proxy the client IP comes from `X-Forwarded-For`.
- **CORS allowlist.** Only origins in `CORS_ALLOWED_ORIGINS` can call it from a
  browser. Add the production domain before launch.

`ip_address` and `user_agent` are stored for abuse triage and are never returned
by the API.

## Editable content

`seed_content` loads the copy that used to live in `frontend/src/data/`. After
that, everything under **Content** in the admin is editable: site settings,
social links, stats, problems, industries, projects, process steps, packages,
team members, testimonials and FAQs. Every list has an `order` column and an `is_published`
tick, both editable straight from the list page.

Feature lists are entered one per line and returned as arrays.

**Team members** (shown on `/team`) take a portrait upload, a role, an optional
short bio, and any of email / WhatsApp / LinkedIn / Facebook / Instagram — only
the ones filled in are shown. A member with no photo renders as initials. The
seeded rows are placeholders; edit or unpublish them.

Two things deliberately stay in the frontend code, because they are design
rather than copy:

- the **mockup themes** — content only names one by key (`themeKey`)
- the **navigation and mega menus**

`seed_content` is safe to re-run; it updates rows in place. `--reset` wipes
content first and discards admin edits.

### How edits reach the site

The frontend fetches `/api/content/` with a 5-minute revalidate, so a change in
the admin appears within five minutes. Pages stay statically rendered.

Two consequences worth knowing:

- **The API must be reachable during `next build`.** If it isn't, the frontend
  falls back to its bundled copy and bakes that into the static pages.
- If the API is down at runtime the site keeps serving its last render, and a
  fresh render falls back to the bundled copy rather than failing.

For instant updates instead of a 5-minute wait, add an on-demand revalidation
route in Next and call it from a `post_save` signal here.

## Tests

```bash
./.venv/Scripts/python.exe manage.py test
```

34 tests covering enquiry validation, the honeypot, the rate limit, proxy IP
capture, content serialisation, publish/order filtering, slug generation, team
social-link assembly and the idempotency of `seed_content`.

## Before deploying

1. Set `DJANGO_SECRET_KEY` — startup refuses to run with `DJANGO_DEBUG=False`
   and the placeholder key still in place.
2. Set `DJANGO_DEBUG=False` and list the real host in `DJANGO_ALLOWED_HOSTS`.
3. Add the live site origin to `CORS_ALLOWED_ORIGINS`.
4. Set the `POSTGRES_*` variables to move off SQLite, and uncomment `psycopg` in
   `requirements.txt`.
5. Run `manage.py collectstatic` so the admin and Jazzmin have their CSS.
   Uploaded team photos live in `MEDIA_ROOT`; serve `/media/` from the web
   server or object storage, since Django only serves it when `DEBUG` is on.
6. Set `SITE_URL` so the admin's "View site" link points at the live site.

## Not built yet

Nothing emails you when an enquiry arrives — you have to open the admin. Adding
that means SMTP settings plus a `post_save` hook or a Celery task.
