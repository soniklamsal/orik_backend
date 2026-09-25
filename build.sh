#!/usr/bin/env bash
# Render runs this on every deploy. Any non-zero exit fails the build.
set -o errexit

pip install -r requirements.txt

# Collect admin + Jazzmin assets for WhiteNoise to serve.
python manage.py collectstatic --no-input

# Schema first, then the starting copy. seed_content only fills gaps, so it
# never overwrites wording edited in the admin.
python manage.py migrate
python manage.py seed_content

# Creates the admin login on first deploy if DJANGO_SUPERUSER_* are set.
python manage.py ensure_superuser
