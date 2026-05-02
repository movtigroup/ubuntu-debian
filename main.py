import random
import asyncio
import time
import logging
from typing import Dict, List, Optional, Tuple, AsyncIterator, Any
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx

# --- تنظیمات Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Smart Mirror Proxy", version="1.2")

# --- پیکربندی اولیه ---
# لیست آینه‌ها برای Ubuntu و Debian
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
    "http://repo.iut.ac.ir/debian",
    "https://mirror.iranserver.com/debian",
    "https://mirror.shatel.ir/debian",
    "https://repo.hmirror.ir/debian",
    "http://linux-mirror.liara.ir/repository/debian",
    "http://mirror.arvancloud.ir/debian",
    "https://repo.abrha.net/debian",
    "https://mirror.mobinhost.com/debian",
    "https://mirrors.pardisco.co/debian",
    "https://mirror2.chabokan.net/debian",
    "http://deb.debian.org/debian",
    "http://ftp.debian.org/debian",
]

# مسیرهایی که برای بررسی سلامت آینه‌ها استفاده می‌شوند
HEALTH_CHECK_PATHS = ["/dists/stable/Release", "/project/trace", "/ls-lR.gz"]
HEALTH_CHECK_TIMEOUT = 15.0  # ثانیه
HEALTH_CHECK_INTERVAL = 120  # ثانیه (هر 2 دقیقه)

# --- کلاس مدیریت استخر آینه‌ها ---
class MirrorPool:
    def __init__(self, mirrors: List[str], name: str):
        self.name = name
        self.mirrors_config = mirrors # لیست اصلی آینه‌ها
        self.clients: Dict[str, httpx.AsyncClient] = {} # نگهداری کلاینت‌ها برای هر mirror
        self.health: Dict[str, Dict] = {} # وضعیت سلامت و لتنسی هر mirror
        self.healthy_mirrors: List[str] = [] # لیست آینه‌هایی که سالم تشخیص داده شده‌اند
        self.lock = asyncio.Lock()
        self.unhealthy_streak: Dict[str, int] = {} # شمارنده خطاهای متوالی برای هر mirror
        self.streak_threshold = 5 # تعداد خطای متوالی قبل از حذف موقت

    async def _create_client(self, mirror_url: str) -> httpx.AsyncClient:
        """یک کلاینت httpx برای یک Mirror ایجاد می‌کند."""
        if mirror_url in self.clients and not self.clients[mirror_url].is_closed:
            return self.clients[mirror_url]
        
        try:
            # تنظیمات کلاینت: timeout های مناسب، verify=False برای سازگاری با بعضی Mirror ها
            # max_keepalive_connections برای مدیریت بهتر اتصالات
            client = httpx.AsyncClient(
                timeout=httpx.Timeout(HEALTH_CHECK_TIMEOUT, read=HEALTH_CHECK_TIMEOUT),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=5),
                verify=False # اگر مشکلی با SSL داشتید، این خط را بردارید
            )
            self.clients[mirror_url] = client
            logger.info(f"{self.name}: Created client for {mirror_url}")
            return client
        except Exception as e:
            logger.error(f"{self.name}: Error creating client for {mirror_url}: {e}")
            return None

    async def _close_client(self, mirror_url: str):
        """کلاینت httpx مربوط به یک Mirror را می‌بندد."""
        if mirror_url in self.clients:
            try:
                await self.clients[mirror_url].aclose()
                del self.clients[mirror_url]
                logger.info(f"{self.name}: Closed client for {mirror_url}")
            except Exception as e:
                logger.error(f"{self.name}: Error closing client for {mirror_url}: {e}")

    async def health_check_single_mirror(self, client: httpx.AsyncClient, mirror_url: str) -> Tuple[str, Dict]:
        """سلامت یک Mirror را با تلاش برای دسترسی به مسیرهای مختلف بررسی می‌کند."""
        start_time = time.monotonic()
        is_healthy = False
        latency = None
        status_details = "down"

        if mirror_url not in self.clients or self.clients[mirror_url].is_closed:
            # اگر کلاینت وجود ندارد یا بسته شده، یکی جدید بساز
            client_for_check = await self._create_client(mirror_url)
            if client_for_check is None:
                return mirror_url, {"status": "error_client", "latency": None}
        else:
            client_for_check = client # استفاده از کلاینت ورودی

        for path in HEALTH_CHECK_PATHS:
            check_url = f"{mirror_url.rstrip('/')}{path}"
            try:
                resp = await client_for_check.get(check_url, timeout=HEALTH_CHECK_TIMEOUT, follow_redirects=True)
                if resp.status_code == 200:
                    latency = round(time.monotonic() - start_time, 3)
                    is_healthy = True
                    status_details = f"up (latency: {latency}s)"
                    break # اگر یک مسیر سالم بود، کافیست
            except (httpx.RequestError, asyncio.TimeoutError) as e:
                # logger.debug(f"Health check failed for {check_url}: {e}") # برای دیباگ عمیق تر
                continue # تلاش برای مسیر بعدی

        health_data = {"status": status_details, "latency": latency}
        return mirror_url, health_data

    async def run_health_check(self):
        """تمام آینه‌ها را بررسی کرده و لیست سلامت را به‌روز می‌کند."""
        async with self.lock:
            current_healthy_mirrors = list(self.healthy_mirrors) # کپی برای پردازش
            current_unhealthy_streak = self.unhealthy_streak.copy()
            
            # اطمینان از وجود کلاینت برای هر آینه قبل از چک کردن
            for mirror in self.mirrors_config:
                if mirror not in self.clients or self.clients[mirror].is_closed:
                    await self._create_client(mirror) # فقط تلاش برای ساخت کلاینت

        # استفاده از کلاینت مشترک برای چک کردن تمام آینه‌ها
        # این یک کلاینت موقت است که فقط برای همین چک استفاده می‌شود
        async with httpx.AsyncClient(verify=False, timeout=HEALTH_CHECK_TIMEOUT) as temp_client:
            tasks = [self.health_check_single_mirror(temp_client, m) for m in self.mirrors_config]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        new_healthy_mirrors = []
        updated_health_data = {}
        updated_unhealthy_streak = {}

        for res in results:
            if isinstance(res, Tuple) and len(res) == 2:
                mirror_url, health_info = res
                updated_health_data[mirror_url] = health_info
                
                if health_info["status"].startswith("up"):
                    new_healthy_mirrors.append(mirror_url)
                    # اگر آینه سالم شد، استریک خطا را ریست کن
                    if mirror_url in current_unhealthy_streak:
                        logger.info(f"{self.name}: Mirror {mirror_url} is healthy again, resetting streak.")
                        # اگر کلاینت داشتیم ببندیم (این قسمت شاید لازم نباشد اگر کلاینت ها پایدار باشند)
                        # await self._close_client(mirror_url) 
                else:
                    # آینه سالم نبود، استریک خطا را افزایش بده
                    streak = current_unhealthy_streak.get(mirror_url, 0) + 1
                    updated_unhealthy_streak[mirror_url] = streak
                    logger.warning(f"{self.name}: Mirror {mirror_url} is down. Streak: {streak}")
                    # اگر آینه به حد نصاب خطا رسید، کلاینت آن را ببندید
                    if streak >= self.streak_threshold:
                        logger.warning(f"{self.name}: Mirror {mirror_url} exceeded streak threshold ({self.streak_threshold}), closing its client.")
                        await self._close_client(mirror_url)
                        # این آینه را از لیست پرواکسی فعلی حذف کن
                        # (اما config آن هنوز باقی می ماند برای تست های بعدی)
            else:
                # خطا در پردازش نتیجه
                mirror_url = str(res) if isinstance(res, Exception) else "unknown"
                updated_health_data[mirror_url] = {"status": "error_processing", "latency": None}
                
        async with self.lock:
            # اولویت با آینه‌هایی است که کلاینتشان فعال است
            final_healthy_mirrors = [m for m in new_healthy_mirrors if m in self.clients]
            
            # fallback: اگر هیچ آینه‌ای سالم نبود، سعی کن از آینه‌هایی که کلاینتشان هنوز فعال است استفاده کنی
            if not final_healthy_mirrors and self.mirrors_config:
                 fallback_mirrors = [m for m in self.mirrors_config if m in self.clients]
                 if fallback_mirrors:
                     final_healthy_mirrors = fallback_mirrors
                     logger.warning(f"{self.name}: No mirrors explicitly healthy, using active clients as fallback.")
                 else:
                     # اگر هیچ کلاینتی هم فعال نبود (همه حذف شدند)
                     logger.error(f"{self.name}: All mirrors have been removed or failed, proxy unavailable.")
                     
            self.healthy_mirrors = final_healthy_mirrors
            self.health = updated_health_data
            self.unhealthy_streak = updated_unhealthy_streak

        logger.info(f"{self.name}: {len(self.healthy_mirrors)}/{len(self.mirrors_config)} mirrors healthy. Health status: {self.health}")

    async def proxy_request(self, request: Request) -> Response:
        """
        درخواست را به یکی از آینه‌های سالم پرواکسی می‌کند.
        """
        async with self.lock:
            mirrors_to_try = list(self.healthy_mirrors)
        
        if not mirrors_to_try:
            logger.error(f"{self.name}: No healthy mirrors available for proxying.")
            return Response(content="No healthy mirrors available", status_code=503, media_type="text/plain")

        random.shuffle(mirrors_to_try)  # برای Load Balancing

        # ---- تعریف تابع کمکی برای استریم پاسخ ----
        async def stream_content(resp: httpx.Response) -> AsyncIterator[bytes]:
            """
            بدنه پاسخ را به صورت تکه‌تکه استریم کرده و منابع را آزاد می‌کند.
            """
            try:
                async for chunk in resp.aiter_bytes():
                    yield chunk
            except Exception as e:
                logger.error(f"{self.name}: Error streaming response chunk: {e}")
            finally:
                await resp.aclose() # اطمینان از بسته شدن پاسخ و آزاد شدن منابع
        # ---- پایان تابع کمکی ----

        for mirror_url in mirrors_to_try:
            client = self.clients.get(mirror_url)
            if client is None or client.is_closed:
                logger.warning(f"{self.name}: Client for {mirror_url} not available or closed, skipping.")
                continue # آینه سالم بود ولی کلاینتش بسته شده، برو سراغ بعدی

            # آماده سازی URL و هدرها
            target_path = request.url.path.replace(f"/{self.name.lower()}", "", 1) # حذف مسیر پایه پرواکسی
            target_url = f"{mirror_url.rstrip('/')}{target_path}"
            if request.url.query:
                target_url += f"?{request.url.query}"

            # کپی کردن هدرهای اصلی درخواست
            headers = dict(request.headers)
            # هدرهای مورد نیاز برای پرواکسی
            # Host header را باید به mirror فرستاد
            parsed_mirror = urlparse(mirror_url)
            host_header = parsed_mirror.hostname
            if parsed_mirror.port:
                host_header += f":{parsed_mirror.port}"
            headers["host"] = host_header
            
            # حذف هدرهای غیرضروری یا تداخلی
            headers.pop("connection", None)
            headers.pop("transfer-encoding", None) # httpx این را به صورت خودکار مدیریت می‌کند
            headers.pop("accept-encoding", None)    # برای اینکه mirror همیشه content اصلی را بدهد
            headers.pop("proxy-connection", None)
            headers.pop("proxy-authenticate", None)
            headers.pop("proxy-authorization", None)
            headers.pop("te", None)
            headers.pop("trailers", None)
            headers.pop("upgrade", None)
            # حذف هدرهای X- که ممکن است توسط پرواکسی‌های قبلی اضافه شده باشند
            for header_name in list(headers.keys()):
                if header_name.lower().startswith("x-"):
                    del headers[header_name]

            logger.info(f"{self.name} ({mirror_url}): Proxying {request.method} {target_url}")

            try:
                # خواندن بدنه درخواست به صورت Stream
                # برای متدهای POST, PUT, PATCH و ...
                # برای GET و HEAD، body_stream خالی خواهد بود
                
                # اگر متد نیاز به بدنه دارد (POST, PUT, PATCH)
                if request.method in ("POST", "PUT", "PATCH"):
                    # ---- تغییر: استفاده از request.stream() ----
                    request_body_stream = request.stream()
                    # ---- پایان تغییر ----
                else:
                    request_body_stream = None # برای متدهای GET/HEAD و ...

                # ساخت و ارسال درخواست به mirror
                # استفاده از stream=True برای مدیریت پاسخ‌های حجیم
                req = client.build_request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    # اگر request_body_stream وجود دارد، آن را به عنوان محتوا ارسال کن
                    content=request_body_stream, 
                )
                resp = await client.send(req, stream=True)

                # اگر Mirror پاسخ خطا داد (>= 400)
                if resp.status_code >= 400:
                    logger.warning(f"{self.name} ({mirror_url}): Received error {resp.status_code} for {target_url}")
                    # ---- تغییر: خواندن بدنه خطا و بستن صریح پاسخ ----
                    error_body = await resp.aread() # خواندن کامل بدنه خطا
                    await resp.aclose() # بستن اتصال پاسخ
                    # ---- پایان تغییر ----
                    
                    # پاسخ خطا را مستقیماً به کاربر برگردان
                    response_headers = self._filter_response_headers(resp.headers)
                    return Response(content=error_body, status_code=resp.status_code, headers=response_headers, media_type=resp.headers.get("content-type"))
                
                # موفقیت: پاسخ Mirror را به صورت Streaming برگردان
                response_headers = self._filter_response_headers(resp.headers)
                
                # ---- تغییر: استفاده از تابع کمکی stream_content برای هر دو حالت 200 و 206 ----
                logger.info(f"{self.name} ({mirror_url}): Received {resp.status_code} for {target_url}")
                return StreamingResponse(
                    content=stream_content(resp),
                    status_code=resp.status_code,
                    headers=response_headers,
                    media_type=resp.headers.get("content-type")
                )
                # ---- پایان تغییر ----

            except (httpx.ReadTimeout, httpx.ConnectTimeout, asyncio.TimeoutError) as e:
                logger.warning(f"{self.name} ({mirror_url}): Timeout or connection error for {target_url}: {e}")
                # Mirror timeout داده، کلاینتش را ببند و این آینه را موقتاً غیرفعال کن
                await self._close_client(mirror_url)
                # به روز رسانی وضعیت سلامت در چرخه بعدی health check انجام می شود
            except httpx.RequestError as e:
                logger.error(f"{self.name} ({mirror_url}): Request error for {target_url}: {e}")
                # خطای کلی در درخواست، کلاینت را ببند
                await self._close_client(mirror_url)
            except Exception as e:
                logger.exception(f"{self.name} ({mirror_url}): Unexpected error during proxying {target_url}: {e}")
                # هر خطای ناشناخته دیگری، کلاینت را ببند
                await self._close_client(mirror_url)

        # اگر حلقه تمام شد و هیچ پاسخی گرفته نشد
        logger.error(f"{self.name}: All mirrors failed to proxy request for {target_path}")
        return Response(content=f"All {self.name} mirrors failed", status_code=502, media_type="text/plain")
    
    def _filter_response_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        هدرهای پاسخ را برای حذف هدرهای تداخلی یا غیرضروری فیلتر می‌کند.
        """
        filtered = {}
        for k, v in headers.items():
            k_lower = k.lower()
            if k_lower not in {
                'transfer-encoding', 'connection', 'keep-alive',
                'proxy-authorization', 'proxy-authenticate',
                'te', 'trailers', 'upgrade', 'content-encoding',
                'content-length'
            }:
                filtered[k] = v
        return filtered

# --- ایجاد استخرها ---
ubuntu_pool = MirrorPool(UBUNTU_MIRRORS, "ubuntu")
debian_pool = MirrorPool(DEBIAN_MIRRORS, "debian")

# --- Health Check دوره‌ای ---
async def health_check_loop():
    """
    به طور مداوم سلامت تمام آینه‌ها را بررسی می‌کند.
    """
    logger.info("Starting periodic health checks...")
    while True:
        # همزمان سلامت هر دو استخر را چک کن
        await asyncio.gather(
            ubuntu_pool.run_health_check(),
            debian_pool.run_health_check()
        )
        await asyncio.sleep(HEALTH_CHECK_INTERVAL)

@app.on_event("startup")
async def startup_event():
    """
    هنگام شروع برنامه، Health Check loop را اجرا می‌کند.
    """
    if not UBUNTU_MIRRORS or not DEBIAN_MIRRORS:
        logger.warning("No Ubuntu or Debian mirrors configured. Proxy may not function correctly.")
    asyncio.create_task(health_check_loop())

@app.on_event("shutdown")
async def shutdown_event():
    """
    هنگام بستن برنامه، تمام کلاینت‌های httpx را می‌بندد.
    """
    logger.info("Shutting down proxy, closing all httpx clients...")
    # لیست تمام کلاینت‌های فعال را جمع آوری کرده و سپس ببندید
    all_clients_to_close = []
    for pool in [ubuntu_pool, debian_pool]:
        for client in pool.clients.values():
            if not client.is_closed:
                all_clients_to_close.append(client.aclose())
    if all_clients_to_close:
        await asyncio.gather(*all_clients_to_close)
    logger.info("All clients closed.")

# --- مدل ورودی برای درخواست‌های POST ---
# این مدل در حال حاضر استفاده نمی‌شود اما ممکن است در آینده مفید باشد
# class ProxyRequest(BaseModel):
#     path: str

# --- Endpointهای اصلی پرواکسی ---
# این Endpoint ها مسئول دریافت درخواست و ارسال آن به MirrorPool مناسب هستند.
# URL پایه (/ubuntu یا /debian) در MirrorPool حذف می‌شود.

@app.api_route("/{pool_name}/{path:path}", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "TRACE", "CONNECT", "PURGE"])
async def smart_proxy(pool_name: str, path: str, request: Request):
    """
    درخواست‌ها را بر اساس pool_name (ubuntu یا debian) به MirrorPool مناسب هدایت می‌کند.
    مسیر فایل در path:path قرار دارد.
    """
    if pool_name == "ubuntu":
        return await ubuntu_pool.proxy_request(request)
    elif pool_name == "debian":
        return await debian_pool.proxy_request(request)
    else:
        raise HTTPException(status_code=404, detail="Unknown mirror pool. Use 'ubuntu' or 'debian'.")

# --- Endpoint وضعیت ---
@app.get("/status")
async def status_endpoint():
    """
    وضعیت سلامت تمام آینه‌ها را نمایش می‌دهد.
    """
    return {
        "ubuntu": {
            "config_count": len(ubuntu_pool.mirrors_config),
            "healthy_count": len(ubuntu_pool.healthy_mirrors),
            "health_details": ubuntu_pool.health,
            "unhealthy_streaks": ubuntu_pool.unhealthy_streak
        },
        "debian": {
            "config_count": len(debian_pool.mirrors_config),
            "healthy_count": len(debian_pool.healthy_mirrors),
            "health_details": debian_pool.health,
            "unhealthy_streaks": debian_pool.unhealthy_streak
        }
    }

# --- اجرای مستقیم (برای تست) ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Smart Mirror Proxy server...")
    # پورت 8000 برای اجرای مستقیم با uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
