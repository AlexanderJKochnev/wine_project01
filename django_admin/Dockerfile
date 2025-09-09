# django_admin/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY ./django_admin/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./.env .
COPY ./django_admin/ .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]