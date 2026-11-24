# Setup Guide

## Prerequisites

- Python 3.12
- pip
- MySQL server and client libraries
- Node.js and npm
- SMTP credentials only if authority approval/rejection email notifications should be sent

<!-- TODO: Add the minimum supported Node.js version if project-level compatibility is known. -->

## 1. Start MySQL

Set the database variables from `.env.example`, export them in your shell, and start MySQL:

```bash
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=<mysql-user>
export MYSQL_PASSWORD=<mysql-password>
export MYSQL_DB=face_recognition_db
```

Create the database and tables:

```bash
cd backend
mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p < db/schema.sql
```

Set placeholder seed-account credentials and run the idempotent seed script:

```bash
export SEED_USER_EMAIL=seed-user@example.invalid
export SEED_USER_PASSWORD=<seed-user-password>
export SEED_AUTHORITY_EMAIL=seed-authority@example.invalid
export SEED_AUTHORITY_PASSWORD=<seed-authority-password>
export SEED_ADMIN_EMAIL=seed-admin@example.invalid
export SEED_ADMIN_PASSWORD=<seed-admin-password>

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

### Railway configuration

If local `backend/app/config.py` cannot load, `backend/config_railway.py` reads these environment variables:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask secret key |
| `JWT_SECRET_KEY` | JWT signing key |
| `MYSQLHOST` | MySQL host |
| `MYSQLUSER` | MySQL user |
| `MYSQLPASSWORD` | MySQL password |
| `MYSQLDATABASE` | MySQL database name |
| `MAIL_PASSWORD` | SMTP password |
| `SEED_USER_EMAIL`, `SEED_USER_PASSWORD` | Placeholder normal-user seed account |
| `SEED_AUTHORITY_EMAIL`, `SEED_AUTHORITY_PASSWORD` | Placeholder authority seed account |
| `SEED_ADMIN_EMAIL`, `SEED_ADMIN_PASSWORD` | Placeholder admin seed account |

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
