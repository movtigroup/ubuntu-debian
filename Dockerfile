FROM python:3.11-slim

WORKDIR /app

# نصب وابستگی‌های سیستم (اختیاری، برای بسته‌های httpx)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# کپی فایل وابستگی‌ها
COPY requirements.txt .

# نصب پکیج‌های پایتون
RUN pip install --no-cache-dir -r requirements.txt

# کپی سورس اپلیکیشن
COPY main.py .

# expose پورت سرویس
EXPOSE 8000

# اجرا با uvicorn (بدون reload برای پروداکشن)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
