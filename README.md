# 📦 Smart Ubuntu & Debian Mirror Proxy

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Mirrors](https://img.shields.io/badge/Mirrors-Iranian-blue?style=for-the-badge)]()

> **پروکسی هوشمند و سبک برای مخازن Ubuntu و Debian**
> با استفاده از آینه‌های داخلی (ایران)، سرعت دانلود بسته‌ها را چندین برابر کنید.
> بدون نیاز به تغییر عادات – فقط کافیست `sources.list` را تنظیم کنید.

این سرویس به صورت آماده روی آدرس `https://mirro.ththt.ir` در دسترس است.
همچنین می‌توانید کد را روی سرور خود اجرا کرده و لیست آینه‌ها را شخصی‌سازی کنید.

---

## ✨ ویژگی‌ها

- **آینه‌های داخلی با کیفیت** – پشتیبانی از بیش از ۱۰ آینه معتبر ایرانی (IUT، آرون‌کلود، آبرا نت، چابوکان و ...)
- **Health Check هوشمند** – هر ۲ دقیقه سلامت آینه‌ها بررسی شده و لیست سالم‌ها به‌روز می‌شود
- **Fallback خودکار** – اگر آینه‌ای پاسخ ندهد، درخواست به آینه سالم بعدی هدایت می‌شود
- **Load Balancing تصادفی** – توزیع بار بین آینه‌های سالم برای پایداری بیشتر
- **ایستا و سریع** – بدون نگهداری state، پاسخ مستقیم از آینه‌ها
- **پشتیبانی همزمان از Ubuntu و Debian** – دو endpoint جداگانه با استخر آینه مجزا
- **وضعیت لحظه‌ای** – endpoint `/status` وضعیت همه آینه‌ها و تأخیر آن‌ها را نمایش می‌دهد
- **بدون Cache** – این پروکسی فایلی را ذخیره نمی‌کند و فقط هدایت می‌کند

---

## 🚀 شروع سریع

### با Docker (توصیه شده)

```bash
git clone https://github.com/movtigroup/ubuntu-debian.git
cd smart-mirror-proxy
docker-compose up -d
```

سرویس روی پورت `8000` در دسترس خواهد بود.

### بدون Docker (نیازمند Python 3.11+)

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📡 نحوه استفاده

### 1️⃣ استفاده به عنوان Proxy APT

فایل `/etc/apt/sources.list` خود را با آدرس پروکسی به‌روز کنید:

**Ubuntu 22.04 (Jammy):**
```bash
deb https://mirro.ththt.ir/ubuntu jammy main restricted universe multiverse
deb https://mirro.ththt.ir/ubuntu jammy-updates main restricted universe multiverse
deb https://mirro.ththt.ir/ubuntu jammy-security main restricted universe multiverse
```

**Debian 12 (Bookworm):**
```bash
deb https://mirro.ththt.ir/debian bookworm main contrib non-free
deb https://mirro.ththt.ir/debian bookworm-updates main contrib non-free
deb https://mirro.ththt.ir/debian bookworm-security main contrib non-free
```

> **توجه:** APT به صورت پیش‌فرض از متد `GET` استفاده می‌کند. اگر از نسخه میزبانی شده (`mirro.ththt.ir`) استفاده می‌کنید، آن سرویس به‌گونه‌ای پیکربندی شده که درخواست‌های `GET` را نیز بپذیرد.
> در صورت اجرای محلی، باید یک Reverse Proxy (مثل Nginx) در جلو قرار دهید که `GET` را به `POST` داخلی تبدیل کند، یا endpoint `GET` به کد اضافه کنید. (در حال حاضر فقط `POST` پشتیبانی می‌شود)

### 2️⃣ درخواست مستقیم (API)

#### دریافت فایل از مخازن Ubuntu
```bash
curl -X POST https://mirro.ththt.ir/ubuntu \
  -H "Content-Type: application/json" \
  -d '{"path": "/dists/jammy/Release"}'
```

#### دریافت فایل از مخازن Debian
```bash
curl -X POST https://mirro.ththt.ir/debian \
  -H "Content-Type: application/json" \
  -d '{"path": "/dists/stable/Release"}'
```

#### مشاهده وضعیت همه آینه‌ها
```bash
curl https://mirro.ththt.ir/status
```

---

## 📋 لیست آینه‌های پشتیبانی‌شده

### Ubuntu

| آینه | پروتکل |
|------|--------|
| `repo.iut.ac.ir/ubuntu` | HTTP |
| `mirror.iranserver.com/ubuntu` | HTTPS |
| `mirror.shatel.ir/ubuntu` | HTTPS |
| `repo.hmirror.ir/ubuntu` | HTTPS |
| `linux-mirror.liara.ir/repository/ubuntu` | HTTP |
| `mirror.arvancloud.ir/ubuntu` | HTTP |
| `repo.abrha.net/ubuntu` | HTTPS |
| `mirror.mobinhost.com/ubuntu` | HTTPS |
| `mirrors.pardisco.co/ubuntu` | HTTPS |
| `mirror2.chabokan.net/ubuntu` | HTTPS |
| `archive.ubuntu.com/ubuntu` | HTTP (پشتیبان جهانی) |

### Debian

| آینه | پروتکل |
|------|--------|
| `repo.iut.ac.ir/debian` | HTTP |
| `mirror.iranserver.com/debian` | HTTPS |
| `mirror.shatel.ir/debian` | HTTPS |
| `repo.hmirror.ir/debian` | HTTPS |
| `linux-mirror.liara.ir/repository/debian` | HTTP |
| `mirror.arvancloud.ir/debian` | HTTP |
| `repo.abrha.net/debian` | HTTPS |
| `mirror.mobinhost.com/debian` | HTTPS |
| `mirrors.pardisco.co/debian` | HTTPS |
| `mirror2.chabokan.net/debian` | HTTPS |
| `deb.debian.org/debian` | HTTP (پشتیبان جهانی) |
| `ftp.debian.org/debian` | HTTP (پشتیبان جهانی) |

> تمام آینه‌های ذکر شده **داخلی (ایران)** هستند و کیفیت بالایی برای کاربران داخل کشور دارند. آینه‌های جهانی تنها به عنوان پشتیبان (fallback) استفاده می‌شوند.

---

## ⚙️ نحوه عملکرد Health Check و Load Balancing

- **Health Check** هر ۱۲۰ ثانیه به صورت خودکار اجرا می‌شود.
- برای بررسی سلامت، سه مسیر `/dists/stable/Release`، `/project/trace` و `/ls-lR.gz` تست می‌شوند.
- آینه‌های سالم در یک استخر قرار می‌گیرند و درخواست‌ها به صورت تصادفی بین آن‌ها توزیع می‌شود.
- اگر هیچ آینه‌ای سالم نباشد، از آخرین آینه موجود در لیست (آینه اصلی جهانی) به عنوان fallback استفاده می‌شود.

> **تغییر تنظیمات:** می‌توانید بازه health check و مسیرهای تست را در فایل `main.py` تغییر دهید.

---

## 🐳 Docker Compose

```yaml
version: '3.8'
services:
  mirror-proxy:
    build: .
    container_name: smart-mirror-proxy
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - TZ=Asia/Tehran
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## 🧰 وابستگی‌ها

- **Python 3.11+**
- **FastAPI** – فریمورک وب
- **httpx** – درخواست‌های HTTP غیرهمزمان
- **uvicorn** – سرور ASGI

---

## 📁 ساختار پروژه

```
.
├── main.py              # کد اصلی سرویس
├── requirements.txt     # وابستگی‌های پایتون
├── Dockerfile           # ساخت ایمیج داکر
├── docker-compose.yml   # اجرای سرویس با داکر
└── README.md            # این فایل
```

---

## 📝 نکات مهم

1. **کیفیت آینه‌های داخلی:** آینه‌های لیست شده همگی با بالاترین کیفیت و پایداری از مراکز داده معتبر ایران انتخاب شده‌اند.
2. **عدم ذخیره‌سازی:** این پروکسی **هیچ فایلی را کش نمی‌کند** و صرفاً درخواست را به آینه سالم هدایت می‌کند.
3. **تحمل خطا:** اگر آینه‌ای دچار مشکل شود، درخواست بلافاصله به آینه بعدی هدایت می‌شود و کاربر متوجه قطعی نخواهد شد.
4. **اندازه پاسخ:** برای دانلود فایل‌های حجیم (مثل ISOs) محدودیتی وجود ندارد.
5. **امنیت:** درخواست‌ها با `verify=False` ارسال می‌شوند تا آینه‌هایی که گواهی SSL نامعتبر دارند هم کار کنند. اگر امنیت بالا نیاز دارید، این گزینه را غیرفعال کنید.
6. **استفاده با APT محلی:** اگر سرویس را به صورت محلی اجرا می‌کنید و می‌خواهید APT مستقیماً از آن استفاده کند، باید یک Reverse Proxy (مانند Nginx) تنظیم کنید تا درخواست‌های `GET` را به `POST` داخلی تبدیل کند. یا endpoint `GET` به کد اضافه کنید.

---

## 🤝 مشارکت

اگر آینه داخلی دیگری می‌شناسید که پایدار است، خوشحال می‌شویم آن را به لیست اضافه کنیم. Pull Request بزنید یا issue ثبت کنید.

---

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است. استفاده آزاد، تجاری و شخصی بلامانع است.
