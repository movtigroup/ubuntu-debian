# 📦 智能 OS 镜像代理 (v2.0)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Mirrors](https://img.shields.io/badge/Mirrors-Multi--OS-orange?style=for-the-badge)]()
[![Releases](https://img.shields.io/github/v/release/movtigroup/ubuntu-debian?style=for-the-badge)](https://github.com/movtigroup/ubuntu-debian/releases)

[English](README.en.md) | [简体中文](README.zh.md) | [فارسی](README.md)

> **适用于 Linux 仓库的智能、多发行版且超快的代理。**
> 智能优先级：第一层（本地镜像），第二层（全球、中国、欧洲、美国镜像）。
> 根据最低延迟自动选择，提供最佳速度体验。

该服务智能地将您的请求引导至最近且最快的镜像。

---

## ✨ 核心特性

- **多发行版支持** – 支持 Ubuntu、Debian、Arch Linux、Alpine 和 CentOS。
- **Docker 仓库支持** – Docker GPG 密钥和软件包的代理。
- **智能优先级（分层系统）** –
  - **第一层 (Tier 1):** 高质量本地镜像（伊朗），以获得最大的内部速度。
  - **第二层 (Tier 2):** 可靠的全球镜像（中国、欧洲 (Hetzner, OVH)、美国 (DigitalOcean, Leaseweb)）作为备用。
- **基于延迟的选择** – 在每个层级，镜像按响应时间排序，并选择最快的镜像。
- **自动标签与发布** – 通过 GitHub Actions 实现自动化版本控制和发布。
- **Docker 发布** – 自动化 Docker 镜像发布到 GitHub Packages (GHCR)。
- **高级健康检查** – 持续后台监控所有镜像的健康状况和速度。

---

## 🚀 快速开始

### 使用 Docker (推荐)

```bash
docker-compose up -d
```

### 不使用 Docker (需要 Python 3.11+)

```bash
pip install -r requirements.txt
python main.py
```

---

## 📡 如何使用

只需将操作系统设置中的仓库 URL 更改为此代理的地址：

### **Ubuntu / Debian**
编辑 `/etc/apt/sources.list`:
```bash
deb http://YOUR_PROXY_IP:8000/ubuntu jammy main restricted
# 或者对于 Debian
deb http://YOUR_PROXY_IP:8000/debian bookworm main
```

### **Docker (Ubuntu / Debian)**
设置 GPG 密钥：
```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL http://YOUR_PROXY_IP:8000/docker/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

将仓库添加到 `sources.list.d`:
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] http://YOUR_PROXY_IP:8000/docker/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### **Arch Linux**
编辑 `/etc/pacman.d/mirrorlist`:
```bash
Server = http://YOUR_PROXY_IP:8000/archlinux/$repo/os/$arch
```

### **Alpine**
编辑 `/etc/apk/repositories`:
```bash
http://YOUR_PROXY_IP:8000/alpine/v3.18/main
```

### **CentOS**
编辑 `/etc/yum.repos.d/` 中的文件并将 `baseurl` 更改为代理地址。

---

## 📋 支持的发行版

- **Ubuntu** (`/ubuntu`)
- **Debian** (`/debian`)
- **Docker** (`/docker`)
- **Arch Linux** (`/archlinux`)
- **Alpine** (`/alpine`)
- **CentOS** (`/centos`)

---

## 🛠 实时状态
查看镜像的健康状态、延迟以及活动镜像列表：
```bash
curl http://YOUR_PROXY_IP:8000/status
```

---

## 📄 许可证
该项目根据 MIT 许可证发布。允许自由和商业使用。
