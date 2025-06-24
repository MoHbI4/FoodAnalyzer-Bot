# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и исходный код
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Гарантируем, что bot.log — это файл, а не директория
RUN rm -rf /app/bot.log && touch /app/bot.log

# Переменная окружения для корректной работы python buffering
ENV PYTHONUNBUFFERED=1

# Команда запуска
CMD ["python", "main.py"]
