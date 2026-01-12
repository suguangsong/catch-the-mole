FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app/backend
# 复制前端构建产物到 static 目录（Django 的 STATICFILES_DIRS）
COPY --from=frontend-builder /app/frontend/dist /app/backend/static

WORKDIR /app/backend

ENV PYTHONPATH=/app/backend
ENV DJANGO_SETTINGS_MODULE=app.settings

# Zeabur 会自动设置 PORT 环境变量，如果没有设置则默认使用 9000
ENV PORT=9000

EXPOSE $PORT

CMD sh -c "gunicorn app.wsgi:application --bind 0.0.0.0:${PORT} --workers 1 --threads 4"
