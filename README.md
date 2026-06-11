# 📦 Smart OS Mirror Proxy (v2.0)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Mirrors](https://img.shields.io/badge/Mirrors-Multi--OS-orange?style=for-the-badge)]()
[![Releases](https://img.shields.io/github/v/release/movtigroup/ubuntu-debian?style=for-the-badge)](https://github.com/movtigroup/ubuntu-debian/releases)

> **پروکسی هوشمند، چند توزیعی و فوق‌سریع برای مخازن لینوکس**
> با سیستم اولویت‌بندی هوشمند: ابتدا آینه‌های ایران، سپس آینه‌های جهانی و چین.
> انتخاب خودکار بر اساس کمترین تاخیر (Latency) برای تجربه بهترین سرعت.

این سرویس به صورت هوشمند درخواست‌های شما را به نزدیک‌ترین و سریع‌ترین آینه هدایت می‌کند.

---

## ✨ ویژگی‌های جدید (v2.0)

- **پشتیبانی از توزیع‌های متنوع** – اضافه شدن Arch Linux، Alpine و CentOS در کنار Ubuntu و Debian.
- **پشتیبانی از مخزن Docker** – قابلیت دریافت کلید GPG و پکیج‌های داکر از طریق پروکسی.
- **سیستم اولویت‌بندی دو مرحله‌ای (Tiered System)** –
  - **Tier 1:** آینه‌های باکیفیت داخلی (ایران) برای ترافیک نیم‌بها و سرعت حداکثری.
  - **Tier 2:** آینه‌های معتبر جهانی (چین، اروپا، آمریکا) در صورت در دسترس نبودن آینه‌های داخلی.
- **انتخاب بر اساس Latency** – در هر مرحله، آینه‌ها بر اساس سرعت پاسخ‌دهی مرتب شده و سریع‌ترین آینه انتخاب می‌شود.
- **Auto Tag & Release** – سیستم انتشار خودکار نسخه‌های جدید با استفاده از GitHub Actions.
- **Health Check پیشرفته** – بررسی مداوم سلامت و سرعت تمام آینه‌ها در پس‌زمینه.

---

## 🚀 شروع سریع

### با Docker (توصیه شده)

```bash
docker-compose up -d
```

### بدون Docker (نیازمند Python 3.11+)

```bash
pip install -r requirements.txt
python main.py
```

---

## 📡 نحوه استفاده

کافیست آدرس مخزن را در تنظیمات سیستم‌عامل خود به آدرس این پروکسی تغییر دهید:

### **Ubuntu / Debian**
فایل `/etc/apt/sources.list`:
```bash
deb http://YOUR_PROXY_IP:8000/ubuntu jammy main restricted
# یا برای دبیان
deb http://YOUR_PROXY_IP:8000/debian bookworm main
```

### **Docker (Ubuntu / Debian)**
تنظیم کلید GPG:
```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL http://YOUR_PROXY_IP:8000/docker/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

اضافه کردن مخزن به `sources.list.d`:
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] http://YOUR_PROXY_IP:8000/docker/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### **Arch Linux**
فایل `/etc/pacman.d/mirrorlist`:
```bash
Server = http://YOUR_PROXY_IP:8000/archlinux/$repo/os/$arch
```

### **Alpine**
فایل `/etc/apk/repositories`:
```bash
http://YOUR_PROXY_IP:8000/alpine/v3.18/main
```

### **CentOS**
فایل‌های موجود در `/etc/yum.repos.d/` را ویرایش کرده و `baseurl` را به آدرس پروکسی تغییر دهید.

---

## 📋 توزیع‌های پشتیبانی شده

- **Ubuntu** (`/ubuntu`)
- **Debian** (`/debian`)
- **Docker** (`/docker`)
- **Arch Linux** (`/archlinux`)
- **Alpine** (`/alpine`)
- **CentOS** (`/centos`)

---

## 🛠 مشاهده وضعیت لحظه‌ای
برای مشاهده وضعیت سلامت آینه‌ها، تاخیر (Latency) هر کدام و لیست آینه‌های فعال:
```bash
curl http://YOUR_PROXY_IP:8000/status
```

---

## 📄 مجوز
این پروژه تحت مجوز MIT منتشر شده است. استفاده آزاد و تجاری بلامانع است.
