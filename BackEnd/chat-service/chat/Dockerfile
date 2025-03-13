FROM python:3.9
ENV PYTHONUNBUFFERED 1

# Створюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо та встановлюємо залежності
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копіюємо весь код проекту
COPY . .

# Встановлюємо змінну середовища для модуля налаштувань
ENV DJANGO_SETTINGS_MODULE=chat.settings