# Setup Guide

## Prerequisites

- Python 3.12
- pip
- MySQL server and client libraries
- Node.js and npm
- SMTP credentials only if authority approval/rejection email notifications should be sent

<!-- TODO: Add the minimum supported Node.js version if project-level compatibility is known. -->

## 1. Start MySQL

Copy the environment template and fill in the placeholders:

```bash
cp .env.example .env
```

`backend/app/config.py` and `backend/db/seed.py` load the repository-root `.env` automatically.

Create the database and tables:

```bash
cd backend
mysql -h 127.0.0.1 -P 3306 -u <mysql-user> -p < db/schema.sql
```

Set the `SEED_*` placeholder credentials in `.env`, then run the idempotent seed script:

```bash
python db/seed.py
```

The schema defines these core tables:

- `users`
- `authority`
- `missing_persons`
- `found_persons`
- `match_results`


## 2. Configure the backend

Run the backend setup from the repository root:

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Local configuration

`backend/app/config.py` is loaded first. Replace development values outside source control and never commit real secrets.

| Name | Purpose |
|---|---|
| `FRONTEND_URL` | Allowed frontend origin |
| `SECRET_KEY` | Flask secret key |
| `MYSQL_HOST` | MySQL host |
| `MYSQL_PORT` | MySQL port |
| `MYSQL_USER` | MySQL user |
| `MYSQL_PASSWORD` | MySQL password |
| `MYSQL_DB` | MySQL database name |
| `JWT_SECRET_KEY` | JWT signing key |
| `JWT_COOKIE_*` settings | Cookie location, SameSite, security, CSRF, and expiry behavior |
| `UPLOAD_FOLDER` | Uploaded-file base folder |
| `MAIL_SERVER` | SMTP server |
| `MAIL_PORT` | SMTP port |
| `MAIL_USE_TLS` | Enable SMTP TLS |
| `MAIL_USERNAME` | SMTP username |
| `MAIL_PASSWORD` | SMTP password |
| `MAIL_DEFAULT_SENDER` | From address for notification emails |
| `ADMIN_EMAIL` | Configured admin email value |

Flask-CORS allows `http://localhost:5173`, `http://127.0.0.1:5173`, `http://127.0.0.1:5174`, and the deployed Vercel frontend origin.

## 3. Start the backend

```bash
cd backend
source venv/bin/activate
python run.py
```

The development server listens at `http://127.0.0.1:5000`.

For Gunicorn-style production startup:

```bash
cd backend
gunicorn run:app
```

The deployment entry is also declared in `backend/Procfile`:

```text
web: gunicorn run:app
```

## 4. Configure and start the frontend

Create or update `frontend/.env`:

```dotenv
VITE_API_URL=http://127.0.0.1:5000
```

`VITE_API_URL` defaults to `http://127.0.0.1:5000` if it is not set.

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Start MySQL and the backend before starting the frontend.

## Accounts

### Normal user

Register through `/signup`, or run `python db/seed.py` to create the placeholder user account from `SEED_USER_*`.

### Authority

Register through `/signup`, or run `python db/seed.py` to create an approved placeholder authority from `SEED_AUTHORITY_*`.

### Admin

Run `python db/seed.py` to create the placeholder admin account from `SEED_ADMIN_*`.

## Testing

No automated test suite or test runner configuration is present.

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

The lint command currently reports existing unused-variable and React hook issues.

Backend smoke check:

```bash
cd backend
python run.py
```

In another terminal:

```bash
curl http://127.0.0.1:5000/
```

The health route returns the Flask status and whether MySQL is connected.

## Troubleshooting

- **Database connection fails:** verify MySQL is running and check `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DB`.
- **Frontend cannot call the API:** verify `VITE_API_URL` and that the frontend origin is allowed by Flask-CORS.
- **Authority cannot log in:** an application must be approved by an admin.
- **Authority email not received:** verify SMTP settings and `MAIL_PASSWORD`, and ensure email delivery is permitted by the provider.
- **Face processing fails:** verify the model files in `backend/models/` and the persisted indexes in `backend/faiss_indexes/`.
- **Backend package installation fails:** use Python 3.12 and the system MySQL development libraries required by `mysqlclient`.
