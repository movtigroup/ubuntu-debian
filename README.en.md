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
