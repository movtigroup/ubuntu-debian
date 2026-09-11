# 📦 Smart OS Mirror Proxy (v2.0)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Mirrors](https://img.shields.io/badge/Mirrors-Multi--OS-orange?style=for-the-badge)]()
[![Releases](https://img.shields.io/github/v/release/movtigroup/ubuntu-debian?style=for-the-badge)](https://github.com/movtigroup/ubuntu-debian/releases)

[English](README.en.md) | [简体中文](README.zh.md) | [فارسی](README.md)

> **Smart, multi-distribution, and ultra-fast proxy for Linux repositories.**
> Intelligent prioritization: Tier 1 (Local mirrors), Tier 2 (Global, China, Europe, US mirrors).
> Automatic selection based on lowest latency for the best speed experience.

This service intelligently directs your requests to the nearest and fastest mirror.

---

## ✨ Key Features

- **Multi-Distribution Support** – Supports Ubuntu, Debian, Arch Linux, Alpine, and CentOS.
- **Docker Repository Support** – Proxy for Docker GPG keys and packages.
- **Intelligent Prioritization (Tiered System)** –
  - **Tier 1:** High-quality local mirrors (Iran) for maximum internal speed.
  - **Tier 2:** Reliable global mirrors (China, Europe (Hetzner, OVH), US (DigitalOcean, Leaseweb)) as failover.
- **Latency-Based Selection** – Mirrors are sorted by response time at each tier, and the fastest is selected.
- **Auto Tag & Release** – Automated versioning and releases via GitHub Actions.
- **Docker Publish** – Automated Docker image publishing to GitHub Packages (GHCR).
- **Advanced Health Check** – Continuous background monitoring of all mirrors' health and speed.

---

## 🚀 Quick Start

### With Docker (Recommended)

```bash
docker-compose up -d
```

### Without Docker (Requires Python 3.11+)

```bash
pip install -r requirements.txt
python main.py
```

---

## 📡 How to Use

Simply change the repository URL in your OS settings to this proxy's address:

### **Ubuntu / Debian**
Edit `/etc/apt/sources.list`:
```bash
deb http://YOUR_PROXY_IP:8000/ubuntu jammy main restricted
# or for Debian
deb http://YOUR_PROXY_IP:8000/debian bookworm main
```

### **Docker (Ubuntu / Debian)**
Setup GPG key:
```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL http://YOUR_PROXY_IP:8000/docker/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

Add repository to `sources.list.d`:
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] http://YOUR_PROXY_IP:8000/docker/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### **Arch Linux**
Edit `/etc/pacman.d/mirrorlist`:
```bash
Server = http://YOUR_PROXY_IP:8000/archlinux/$repo/os/$arch
```

### **Alpine**
Edit `/etc/apk/repositories`:
```bash
http://YOUR_PROXY_IP:8000/alpine/v3.18/main
```

### **CentOS**
Edit files in `/etc/yum.repos.d/` and change `baseurl` to the proxy address.

---

## 🪟 Windows Update Proxy

Due to sanctions, Microsoft's Windows Update servers do not respond to requests from Iranian IPs. You can fetch Windows updates through domestic proxy services instead.

### 📝 Known Windows Update proxies

| Service | Address | Type | Notes |
|---|---|---|---|
| **DevNeeds** | `win.devneeds.ir:8445` | Iran 🇮🇷 | Dedicated Windows Update proxy (recommended) |
| **Microsoft Update Catalog** | `catalog.update.microsoft.com` | Global 🌍 | Direct update downloads (usually not sanctioned) |
| **WSUS Offline Update** | `wsusoffline.com` | Tool 🌍 | Open-source tool for offline update downloads |

> **Note:** No public free foreign Windows Update proxy services exist (updates are unrestricted outside Iran). If you know other Iranian services, please submit a Pull Request to this repository.
>
> ⚠️ **Security notice:** Your update traffic passes through a third-party server. Windows updates are digitally signed by Microsoft, but only use services you trust.

### 🚀 How to configure the proxy for Windows Updates

#### 1. Enable the proxy

Open PowerShell as **Administrator** and set the `proxy` variable:

```powershell
$proxy = "win.devneeds.ir:8445"
```

Then copy and paste the following commands line by line (right-click to paste):

```powershell
netsh winhttp set proxy $proxy

Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyEnable -Value 1
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyServer -Value $proxy
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyOverride -Value ""

Write-Host "Proxy ENABLED"
```

#### 2. Start the update

You can start updating via the GUI at `Settings --> Update & Security`.

Or run the following in PowerShell:

```powershell
Start-Service wuauserv
usoclient StartScan; usoclient StartDownload; usoclient StartInstall
```

#### 3. Disable the proxy (rollback)

> **Note:** Make sure to run PowerShell as Administrator and execute the commands line by line:

```powershell
netsh winhttp reset proxy

Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyEnable -Value 0

Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyServer -ErrorAction SilentlyContinue
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyOverride -ErrorAction SilentlyContinue

Write-Host "Proxy DISABLED (rollback done)"
```

---

## 📋 Supported Distributions

- **Ubuntu** (`/ubuntu`)
- **Debian** (`/debian`)
- **Docker** (`/docker`)
- **Arch Linux** (`/archlinux`)
- **Alpine** (`/alpine`)
- **CentOS** (`/centos`)

---

## 🛠 Real-time Status
To view mirrors' health status, latency, and the list of active mirrors:
```bash
curl http://YOUR_PROXY_IP:8000/status
```

---

## 📄 License
This project is released under the MIT License. Free and commercial use is permitted.
