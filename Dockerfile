# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY src/ ./src/

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///./app.db

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"] 