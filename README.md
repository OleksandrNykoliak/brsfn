# Boristene Django site

## Run locally

```powershell
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Content management

Create an admin account with `python manage.py createsuperuser`, then open
`http://127.0.0.1:8000/admin/` to manage projects, events, partners,
achievements, media mentions, team members and FAQs.

Project pages use the dynamic route `/projects/<slug>/`. The existing
Unbreakable Ukraine presentation remains available at
`/projects/unbreakable-ukraine/` until its final media and source materials are
provided.


## October 2026 UX & content update

See [CHANGES_UA.md](CHANGES_UA.md) for the complete changelog, safe SQLite migration instructions, content population in Django Admin, and verification status. The provided SQLite files remain byte-identical to the source archive.
