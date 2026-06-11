import random
import asyncio
import time
import logging
from typing import Dict, List, Optional, Tuple, AsyncIterator, Any
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
import httpx

from mirrors_data import MIRRORS as MIRRORS_CONFIG

# --- Settings ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Smart Mirror Proxy", version="2.0.0")

HEALTH_CHECK_PATHS = ["/", "/README.html", "/project/trace"]
HEALTH_CHECK_TIMEOUT = 10.0
HEALTH_CHECK_INTERVAL = 120

class MirrorPool:
    def __init__(self, name: str, tiers_config: Dict[str, List[str]]):
        self.name = name
        self.tiers_config = tiers_config
        self.all_mirrors = [m for tier in tiers_config.values() for m in tier]
        self.clients: Dict[str, httpx.AsyncClient] = {}
        self.health: Dict[str, Dict] = {}
        self.healthy_mirrors_by_tier: Dict[str, List[str]] = {tier: [] for tier in tiers_config}
        self.lock = asyncio.Lock()
        self.unhealthy_streak: Dict[str, int] = {}
        self.streak_threshold = 3

    async def _create_client(self, mirror_url: str) -> Optional[httpx.AsyncClient]:
        if mirror_url in self.clients and not self.clients[mirror_url].is_closed:
            return self.clients[mirror_url]
        try:
            client = httpx.AsyncClient(
                timeout=httpx.Timeout(HEALTH_CHECK_TIMEOUT, read=60.0),
                limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
                verify=False
            )
            self.clients[mirror_url] = client
            return client
        except Exception as e:
            logger.error(f"{self.name}: Error creating client for {mirror_url}: {e}")
            return None

    async def _close_client(self, mirror_url: str):
        if mirror_url in self.clients:
            try:
                await self.clients[mirror_url].aclose()
                del self.clients[mirror_url]
            except Exception:
                pass

    async def health_check_single(self, mirror_url: str) -> Tuple[str, Dict]:
        start_time = time.monotonic()
        is_healthy = False
        latency = None

        async with httpx.AsyncClient(verify=False, timeout=5.0) as check_client:
            for path in HEALTH_CHECK_PATHS:
                try:
                    resp = await check_client.get(f"{mirror_url.rstrip('/')}{path}", follow_redirects=True)
                    if resp.status_code < 400:
                        latency = round(time.monotonic() - start_time, 3)
                        is_healthy = True
                        break
                except Exception:
                    continue

        return mirror_url, {"healthy": is_healthy, "latency": latency}

    async def run_health_check(self):
        tasks = [self.health_check_single(m) for m in self.all_mirrors]
        results = await asyncio.gather(*tasks)
        
        new_healthy_by_tier = {tier: [] for tier in self.tiers_config}
        new_health_data = {}

        for mirror_url, data in results:
            new_health_data[mirror_url] = data
            if data["healthy"]:
                self.unhealthy_streak[mirror_url] = 0
                for tier, mirrors in self.tiers_config.items():
                    if mirror_url in mirrors:
                        new_healthy_by_tier[tier].append(mirror_url)
            else:
                self.unhealthy_streak[mirror_url] = self.unhealthy_streak.get(mirror_url, 0) + 1
                if self.unhealthy_streak[mirror_url] >= self.streak_threshold:
                    await self._close_client(mirror_url)

        # Sort by latency within tiers
        for tier in new_healthy_by_tier:
            new_healthy_by_tier[tier].sort(key=lambda m: new_health_data[m]["latency"] or 999)

        async with self.lock:
            self.healthy_mirrors_by_tier = new_healthy_by_tier
            self.health = new_health_data
        
        logger.info(f"{self.name} Health Check: { {t: len(v) for t, v in new_healthy_by_tier.items()} }")

    async def proxy_request(self, request: Request):
        async with self.lock:
            # Prefer Tier 1 (Iran), then Tier 2
            mirrors_to_try = []
            for tier in ["tier1", "tier2"]:
                mirrors_to_try.extend(self.healthy_mirrors_by_tier.get(tier, []))

            if not mirrors_to_try:
                # Emergency fallback to all config
                mirrors_to_try = self.all_mirrors

        async def stream_content(resp):
            try:
                async for chunk in resp.aiter_bytes():
                    yield chunk
            finally:
                await resp.aclose()

        for mirror_url in mirrors_to_try:
            client = await self._create_client(mirror_url)
            if not client: continue

            target_path = request.url.path.replace(f"/{self.name}", "", 1)
            target_url = f"{mirror_url.rstrip('/')}{target_path}"
            if request.url.query:
                target_url += f"?{request.url.query}"

            headers = dict(request.headers)
            parsed = urlparse(mirror_url)
            headers["host"] = parsed.netloc
            for h in ["connection", "transfer-encoding", "accept-encoding"]:
                headers.pop(h, None)

            try:
                req = client.build_request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=request.stream() if request.method in ("POST", "PUT", "PATCH") else None
                )
                resp = await client.send(req, stream=True)

                if resp.status_code >= 400 and mirror_url != mirrors_to_try[-1]:
                    await resp.aclose()
                    continue

                response_headers = {k: v for k, v in resp.headers.items() if k.lower() not in ["content-length", "transfer-encoding", "connection"]}
                return StreamingResponse(
                    stream_content(resp),
                    status_code=resp.status_code,
                    headers=response_headers,
                    media_type=resp.headers.get("content-type")
                )
            except Exception as e:
                logger.warning(f"{self.name} Error with {mirror_url}: {e}")
                continue

        return Response(content="All mirrors failed", status_code=502)

pools: Dict[str, MirrorPool] = {
    name: MirrorPool(name, config) for name, config in MIRRORS_CONFIG.items()
}

@app.on_event("startup")
async def startup():
    async def loop():
        while True:
            await asyncio.gather(*(p.run_health_check() for p in pools.values()))
            await asyncio.sleep(HEALTH_CHECK_INTERVAL)
    asyncio.create_task(loop())

@app.api_route("/{pool_name}/{path:path}", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def smart_proxy(pool_name: str, path: str, request: Request):
    pool = pools.get(pool_name)
    if pool:
        return await pool.proxy_request(request)
    raise HTTPException(status_code=404, detail="Unknown pool")

@app.get("/status")
async def status():
    return {
        name: {
            "healthy": {t: len(v) for t, v in p.healthy_mirrors_by_tier.items()},
            "details": p.health
        } for name, p in pools.items()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
