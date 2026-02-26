# fast-api-Git
password reset API

# Password Reset API

FastAPI приложение для сброса пароля через email.

## Запуск

```bash
docker build -t fast-api-reset .
docker run -p 8000:8000 -v fast_api_data:/app/data fast-api-reset
