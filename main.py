from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import httpx
import asyncio
import random
import time
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Smart Mirror Proxy", version="1.1")

# ======================== لیست آینه‌ها (دستی و کامل) ========================
UBUNTU_MIRRORS = [
    "http://repo.iut.ac.ir/ubuntu",
    "https://mirror.iranserver.com/ubuntu",
    "https://mirror.shatel.ir/ubuntu",
    "https://repo.hmirror.ir/ubuntu",
    "http://linux-mirror.liara.ir/repository/ubuntu",
    "http://mirror.arvancloud.ir/ubuntu",
    "https://repo.abrha.net/ubuntu",
    "https://mirror.mobinhost.com/ubuntu",
    "https://mirrors.pardisco.co/ubuntu",
    "https://mirror2.chabokan.net/ubuntu",
    "http://archive.ubuntu.com/ubuntu",          # پشتیبان جهانی
]

DEBIAN_MIRRORS = [
    # آینه‌هایی که هم ubuntu و هم debian دارند (با تغییر مسیر)
    "http://repo.iut.ac.ir/debian",
    "https://mirror.iranserver.com/debian",
    "https://mirror.shatel.ir/debian",
    "https://repo.hmirror.ir/debian",
    "http://linux-mirror.liara.ir/repository/debian",
    "http://mirror.arvancloud.ir/debian",
    "https://repo.abrha.net/debian",
    "https://mirror.mobinhost.com/debian",
    "https://mirrors.pardisco.co/debian",
    # آینه اختصاصی دبیان که کاربر اشاره کرد
    "https://mirror2.chabokan.net/debian",
    # آینه‌های اصلی جهانی
    "http://deb.debian.org/debian",
    "http://ftp.debian.org/debian",
]

CHECK_PATHS = ["/dists/stable/Release", "/project/trace", "/ls-lR.gz"]

# ======================== کلاس مدیریت استخر آینه‌ها ========================
class MirrorPool:
    def __init__(self, mirrors: List[str], name: str):
        self.name = name
        self.mirrors = mirrors
        self.health: Dict[str, dict] = {}
        self.healthy: List[str] = []
        self.lock = asyncio.Lock()

    async def health_check(self, client: httpx.AsyncClient):
        async def check_one(mirror):
            start = time.monotonic()
            for path in CHECK_PATHS:
                url = f"{mirror.rstrip('/')}{path}"
                try:
                    resp = await client.get(url, timeout=15, follow_redirects=True)
                    if resp.status_code == 200:
                        latency = round(time.monotonic() - start, 3)
                        return {"ok": True, "url": mirror, "latency": latency}
                except Exception:
                    continue
            return {"ok": False, "url": mirror}

        tasks = [check_one(m) for m in self.mirrors]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        healthy = []
        health_data = {}
        for res in results:
            if isinstance(res, dict) and res["ok"]:
                healthy.append(res["url"])
                health_data[res["url"]] = {"status": "up", "latency": res["latency"]}
            else:
                url = res["url"] if isinstance(res, dict) else str(res)
                health_data[url] = {"status": "down", "latency": None}

        async with self.lock:
            self.healthy = healthy if healthy else [self.mirrors[-1]]  # fallback
            self.health = health_data
        logger.info(f"{self.name}: {len(healthy)}/{len(self.mirrors)} mirrors healthy")

    async def proxy(self, client: httpx.AsyncClient, path: str) -> httpx.Response:
        async with self.lock:
            mirrors = list(self.healthy)
        if not mirrors:
            raise HTTPException(status_code=503, detail="No healthy mirrors")

        random.shuffle(mirrors)  # load balancing
        for base in mirrors:
            url = f"{base.rstrip('/')}{path}"
            try:
                resp = await client.get(url, timeout=60, follow_redirects=True)
                if resp.status_code == 200:
                    return resp
                else:
                    logger.warning(f"{base} returned {resp.status_code} for {path}")
                    continue
            except Exception as e:
                logger.warning(f"{base} failed for {path}: {e}")
                continue
        raise HTTPException(status_code=502, detail="All mirrors failed")

# استخر ubuntu و debian
ubuntu_pool = MirrorPool(UBUNTU_MIRRORS, "ubuntu")
debian_pool = MirrorPool(DEBIAN_MIRRORS, "debian")

# ======================== Health Check دوره‌ای ========================
async def health_check_loop():
    async with httpx.AsyncClient(verify=False) as client:
        while True:
            await ubuntu_pool.health_check(client)
            await debian_pool.health_check(client)
            await asyncio.sleep(120)

@app.on_event("startup")
async def startup():
    asyncio.create_task(health_check_loop())

# ======================== مدل ورودی ========================
class ProxyRequest(BaseModel):
    path: str

# ======================== Endpointهای اصلی ========================
@app.post("/ubuntu")
async def ubuntu_proxy(req: ProxyRequest):
    async with httpx.AsyncClient(verify=False) as client:
        resp = await ubuntu_pool.proxy(client, req.path)
    content = resp.content
    headers = {k: v for k, v in resp.headers.items()
               if k.lower() not in {'transfer-encoding', 'connection', 'keep-alive',
                                    'proxy-authorization', 'proxy-authenticate',
                                    'te', 'trailers', 'upgrade'}}
    return Response(content=content, status_code=resp.status_code, headers=headers)

@app.post("/debian")
async def debian_proxy(req: ProxyRequest):
    async with httpx.AsyncClient(verify=False) as client:
        resp = await debian_pool.proxy(client, req.path)
    content = resp.content
    headers = {k: v for k, v in resp.headers.items()
               if k.lower() not in {'transfer-encoding', 'connection', 'keep-alive',
                                    'proxy-authorization', 'proxy-authenticate',
                                    'te', 'trailers', 'upgrade'}}
    return Response(content=content, status_code=resp.status_code, headers=headers)

# ======================== وضعیت ========================
@app.get("/status")
async def status():
    return {
        "ubuntu": ubuntu_pool.health,
        "debian": debian_pool.health,
        "ubuntu_healthy_count": len(ubuntu_pool.healthy),
        "debian_healthy_count": len(debian_pool.healthy),
        "total_ubuntu": len(ubuntu_pool.mirrors),
        "total_debian": len(debian_pool.mirrors)
    }

# ======================== اجرای مستقیم ========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
