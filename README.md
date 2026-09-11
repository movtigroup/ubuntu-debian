# 📦 Smart OS Mirror Proxy

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Mirrors](https://img.shields.io/badge/Mirrors-Multi--OS-orange?style=for-the-badge)]()
[![Releases](https://img.shields.io/github/v/release/movtigroup/ubuntu-debian?style=for-the-badge)](https://github.com/movtigroup/ubuntu-debian/releases)

[English](README.en.md) | [简体中文](README.zh.md) | [فارسی](README.md)

> **پروکسی هوشمند، چند توزیعی و فوق‌سریع برای مخازن لینوکس**
> با سیستم اولویت‌بندی هوشمند: ابتدا آینه‌های ایران، سپس آینه‌های جهانی، چین، اروپا و آمریکا.
> انتخاب خودکار بر اساس کمترین تاخیر (Latency) برای تجربه بهترین سرعت.

این سرویس به صورت هوشمند درخواست‌های شما را به نزدیک‌ترین و سریع‌ترین آینه هدایت می‌کند.

---

## ✨ ویژگی‌های کلیدی

- **پشتیبانی از توزیع‌های متنوع** – پشتیبانی از Ubuntu، Debian، Arch Linux، Alpine و CentOS.
- **پشتیبانی از مخزن Docker** – قابلیت دریافت کلید GPG و پکیج‌های داکر از طریق پروکسی.
- **سیستم اولویت‌بندی هوشمند (Tiered System)** –
  - **Tier 1:** آینه‌های باکیفیت داخلی (ایران) برای ترافیک نیم‌بها و سرعت حداکثری.
  - **Tier 2:** آینه‌های معتبر جهانی (چین، اروپا (Hetzner, OVH)، آمریکا (DigitalOcean, Leaseweb)) در صورت در دسترس نبودن آینه‌های داخلی.
- **انتخاب بر اساس Latency** – در هر مرحله، آینه‌ها بر اساس سرعت پاسخ‌دهی مرتب شده و سریع‌ترین آینه انتخاب می‌شود.
- **Auto Tag & Release** – سیستم انتشار خودکار نسخه‌های جدید با استفاده از GitHub Actions.
- **Docker Publish** – انتشار خودکار تصاویر Docker در GitHub Packages (GHCR).
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

## 🪟 پروکسی آپدیت ویندوز (Windows Update)

به دلیل تحریم‌ها، سرورهای Windows Update مایکروسافت به درخواست‌های IPهای ایران پاسخ نمی‌دهند. برای دریافت آپدیت‌های ویندوز می‌توانید از پروکسی‌های داخلی استفاده کنید. این بخش آموزش تنظیم پروکسی و لیست آینه‌های شناخته‌شده را ارائه می‌دهد.

### 📝 لیست پروکسی‌های شناخته‌شده آپدیت ویندوز

| سرویس | آدرس | نوع | توضیحات |
|---|---|---|---|
| **DevNeeds** | `win.devneeds.ir:8445` | ایران 🇮🇷 | پروکسی اختصاصی Windows Update (توصیه شده) |
| **Microsoft Update Catalog** | `catalog.update.microsoft.com` | جهانی 🌍 | دانلود مستقیم آپدیت‌ها (معمولاً بدون تحریم) |
| **WSUS Offline Update** | `wsusoffline.com` | ابزار 🌍 | ابزار متن‌باز برای دانلود آفلاین آپدیت‌ها |

> **نکته:** سرویس عمومی و رایگان مشابه برای پروکسی آپدیت ویندوز در خارج از ایران وجود ندارد (چون آپدیت ویندوز در خارج از ایران بدون محدودیت است). اگر از سرویس‌های ایرانی دیگری استفاده می‌کنید، لطفاً در این مخزن Pull Request ثبت کنید.
>
> ⚠️ **هشدار امنیتی:** ترافیک آپدیت شما از سرور شخص ثالث عبور می‌کند. آپدیت‌های ویندوز توسط مایکروسافت امضای دیجیتال می‌شوند، اما بهتر است فقط از سرویس‌های معتبر استفاده کنید.

### 🚀 آموزش تنظیم پراکسی برای دریافت آپدیت‌های ویندوز

#### ۱. فعال‌سازی پراکسی

در ابتدا ابزار PowerShell را با دسترسی **Administrator** در سیستم خود اجرا کنید و متغیر `proxy` را با استفاده از دستور زیر تنظیم کنید:

```powershell
$proxy = "win.devneeds.ir:8445"
```

سپس دستورات زیر را خط به خط کپی کرده و در PowerShell جایگذاری کنید (می‌توانید با استفاده از کلیک راست، جایگذاری را انجام دهید):

```powershell
netsh winhttp set proxy $proxy

Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyEnable -Value 1
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyServer -Value $proxy
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyOverride -Value ""

Write-Host "Proxy ENABLED"
```

#### ۲. شروع روند بروزرسانی

روند بروزرسانی را می‌توانید با استفاده از رابط گرافیکی از مسیر `Settings --> Update & Security` شروع کنید.

یا با وارد کردن دستور زیر در محیط PowerShell، فرآیند بروزرسانی را شروع کنید:

```powershell
Start-Service wuauserv
usoclient StartScan; usoclient StartDownload; usoclient StartInstall
```

#### ۳. غیرفعال‌سازی پراکسی (بازگردانی)

غیرفعال‌سازی پراکسی با تنظیم مقادیر زیر در PowerShell انجام می‌شود.

> **نکته:** حتماً دقت داشته باشید که PowerShell را با دسترسی Administrator و خط به خط اجرا کنید:

```powershell
netsh winhttp reset proxy

Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyEnable -Value 0

Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyServer -ErrorAction SilentlyContinue
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyOverride -ErrorAction SilentlyContinue

Write-Host "Proxy DISABLED (rollback done)"
```

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
