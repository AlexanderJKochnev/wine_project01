# Dockerfile
FROM python:3.12-slim
# slim ?
ARG APP_PORT
ARG APP_HOST
ENV APP_PORT=${WEB_PORT}
ENV APP_HOST=${WEB_HOST}

WORKDIR /app

COPY requirements.txt .
ENV PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE $APP_PORT
# EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "$APP_HOST", "--port", "$APP_PORT", "--reload"]