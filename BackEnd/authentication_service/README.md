# Authentication service

## Overview
This service handles JWT-based user authentication and role management.

### Setup

Clone the repository:
``
git clone https://github.com/ITA-Dnipro/Forum_UPD.git
cd BackEnd
cd authentication_service
``

Configure .env file in BackEnd/authentication_service:
``
SECRET_KEY=

JWT_SECRET=

#Postgres
POSTGRES_USER=auth_user
POSTGRES_PASSWORD=
POSTGRES_DB=auth_db
POSTGRES_PORT=5432

#SMTP
EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
EMAIL_HOST='localhost'
EMAIL_PORT=1025
EMAIL_USE_TLS=1
EMAIL_HOST_USER=forumprojectstageua@gmail.com
EMAIL_HOST_PASSWORD=

#origin hostnames allowed to make cross-site HTTP requests
CORS_ALLOWED_ORIGINS="http://localhost:8080"

DEBUG=True

ALLOWED_ENV_HOST=http://localhost:8080

REACT_APP_RECAPTCHA_V2_SITE_KEY=

RECAPTCHA_V2_PRIVATE_KEY=

RECAPTCHA_URL=https://www.google.com/recaptcha/api/siteverify

DJANGO_SETTINGS_MODULE = "authentication.settings"
``

Build and run Docker containers:
``
docker compose -f docker-compose.auth.yml up --build
``

## API Documentation

Swagger UI: `http://127.0.0.1:8000/swagger/`

## Testing

Run tests:
``
python manage.py test --settings=authentication.test_setting
``
