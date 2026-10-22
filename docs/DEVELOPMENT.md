# Run the UniSphere foundation

This branch contains the first working Django milestone. It uses fictional accounts and records. The full PRD remains the target for later milestones.

## Requirements

- Python 3.12, Git and a browser.
- VS Code is the suggested editor.
- Node.js 22 is needed only when changing or rebuilding Tailwind styles. Compiled CSS is committed so the initial demo can run without Node.
- PostgreSQL is the target database. SQLite is available for a quick local demonstration; PostgreSQL can run through the optional Compose configuration.

## Windows quick start

Open PowerShell in the project folder. Using the virtual environment's Python directly avoids changing PowerShell's execution policy.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/. Select Student, Lecturer or Admin and use the matching username: `student`, `lecturer` or `admin`. The seeding command prints a generated initial password for newly created demo accounts. Existing passwords are retained when seeding again. Never put the password in GitHub or public screenshots.

## macOS or Linux quick start

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py runserver
```

## PostgreSQL development option

Install Docker with Compose if choosing this option. Set `UNISPHERE_DB_PASSWORD` to a locally generated password, start `docker compose up -d db`, then set `DATABASE_URL` to `postgresql://unisphere:PASSWORD@127.0.0.1:5432/unisphere`, substituting the actual password with URL escaping if needed. Run migrations and seeding against that database. The password is supplied through the environment; Compose does not hard-code it.

Switching database configuration starts with that database's own records. It does not transfer an existing SQLite database. GitHub Actions is configured to execute the same test suite against both engines.

## What works in this milestone

- Student and Lecturer entry choices, with a smaller Admin choice below.
- Real session sign-in, role checks, logout and account deactivation.
- Student dashboard calculations from stored records; attendance, released historical results, sample fee balances and class timetable.
- Enrolled subject pages and protected material downloads.
- Lecturer assignment drafts and publication, PDF/text submission, versioned receipts, draft marks and explicit feedback release.
- Lecturer overview and attendance/outstanding-work filters for assigned classes.
- Admin dashboard and Django administration for users, offerings, enrolments and class schedules. Attendance and audit entries are read-only in this milestone.
- Bottom-right record helper with authorised, deterministic lookups. This is **not yet a model-powered AI teacher**.
- PWA manifest, app icons, service worker and a public offline notice. The worker does not cache academic pages, API responses, uploads or downloads.

The seed provides 20 students, two lecturers, one admin, three current offerings, original text notes, 25 recorded sessions per student and sample historical results. Dates are created relative to the first seed. Counts and assignment states update as records change; re-running seed does not erase work or move deadlines.

## Demonstrate the assignment workflow

1. Sign in as Lecturer. Create an assignment for an assigned offering and publish it.
2. Sign out and sign in as Student. Open Assignments, submit a PDF or UTF-8 text file of up to 5 MB and inspect the receipt.
3. Sign in as Lecturer. Open the submission, save draft feedback, then explicitly release it.
4. Sign in as Student and open that assignment to see the released mark and feedback.
5. Sign in as Admin to inspect operational activity and manage users or enrolments.

Each accepted upload creates a new version. The receipt uses the server timestamp; late uploads are labelled or rejected according to the assignment's setting. Extensions and richer late-submission rules remain future work.

## Checks and styles

```bash
npm ci
npm run build:css
python manage.py collectstatic --noinput
python manage.py check --fail-level WARNING
python manage.py makemigrations --check --dry-run
python manage.py test core
```

Collect static assets before tests because tests exercise the production static manifest as well. Edit `frontend/source.css`, then rebuild `static/css/app.css`. No runtime CDN is required. Run `npm run watch:css` while editing styles.

## PWA behaviour

Installation requires a supporting browser and a secure context (HTTPS, or localhost for development). The Install app button opens the browser's prompt when available or shows platform instructions. Installation has not been certified on physical iOS or Android devices in this milestone.

The offline notice contains no account name or academic data. Private pages use `Cache-Control: private, no-store`. Cache versions derive from the compiled CSS and JavaScript, so asset changes update the worker. Offline submission, AI responses and live quizzes are not supported.

## Remaining milestones

Model-backed AI retrieval and tutoring, recordings/transcripts, Quiz Me, live quizzes, tickets and real test-mailbox notifications, attendance editing/corrections, exam scheduling, programme structure, complete semester/repeat-result policies and simulated payment workflows remain to be implemented. The full Project 1 acceptance milestone is not complete until its remaining AI requirements and evaluation are met.

## Before public deployment

Set `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, the production `DATABASE_URL` and any required `DJANGO_CSRF_TRUSTED_ORIGINS`. Use HTTPS, a shared rate-limit/cache backend, private persistent file storage and an appropriate production server. `runserver` and the default local storage/cache are development choices. No provider credentials or real student data are included.

The local secret, database, uploads and dependencies are ignored by Git. Upload validation in this milestone checks allowed extensions, size and basic format; it is not malware scanning. Hosting and external provider accounts have not been configured by this change.
