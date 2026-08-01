# Базовый образ с уже установленным Python
FROM python:3.13-slim-bookworm

# Аргументы сборки (можно переопределять при docker build)
ARG BASE_URL=http://localhost:4111/api/v1
ARG UI_BASE_URL=http://localhost

# Переменные окружения внутри контейнера
ENV BASE_URL=${BASE_URL}
ENV UI_BASE_URL=${UI_BASE_URL}
ENV PLAYWRIGHT_TEST_BASE_URL=${UI_BASE_URL}

# Рабочая директория
WORKDIR /app

# Сначала копируем только зависимости — для кеширования
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && playwright install-deps
RUN playwright install

# Копируем весь проект
COPY . .

# На случай проблем с правами
USER root

# Запуск тестов + логирование
CMD pytest


