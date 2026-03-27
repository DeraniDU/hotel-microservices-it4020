from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api-gateway")

app = FastAPI(
    title="Hotel Management — API Gateway",
    description="""
    ## 🏨 Hotel Microservices API Gateway
    Single entry point for all hotel microservices.
    All routes are proxied through **port 8000**.

    | Service     | Route Prefix     | Direct Port |
    |-------------|-----------------|-------------|
    | Guest       | /guests/...      | 8001        |
    | Room        | /rooms/...       | 8002        |
    | Booking     | /bookings/...    | 8003        |
    | Payment     | /payments/...    | 8004        |
    | Restaurant  | /restaurant/...  | 8005        |
    | Staff       | /staff/...       | 8006        |
    """,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = {
    "guests":     "http://localhost:8001",
    "rooms":      "http://localhost:8002",
    "bookings":   "http://localhost:8003",
    "payments":   "http://localhost:8004",
    "restaurant": "http://localhost:8005",
    "staff":      "http://localhost:8006",
}

@app.get("/", tags=["Gateway"])
def root():
    return {
        "message": "🏨 Hotel Management API Gateway",
        "version": "1.0.0",
        "services": {k: f"http://localhost:8000/{k}" for k in SERVICES}
    }

@app.get("/health", tags=["Gateway"])
async def health_check():
    """Check which services are online."""
    status = {}
    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, url in SERVICES.items():
            try:
                r = await client.get(f"{url}/health")
                status[name] = "online" if r.status_code == 200 else "degraded"
            except Exception:
                status[name] = "offline"
    return {"gateway": "online", "services": status}

@app.api_route(
    "/{service}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Proxy"],
    summary="Route request to the appropriate microservice root",
)
@app.api_route(
    "/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Proxy"],
    summary="Route request to the appropriate microservice",
)
async def proxy(service: str, request: Request, path: str = ""):
    if service not in SERVICES:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service}' not found. Available: {list(SERVICES.keys())}"
        )

    # If no subpath is provided (e.g. /staff), forward to the service's
    # resource root (/staff) instead of service root (/)
    target_url = f"{SERVICES[service]}/{path}" if path else f"{SERVICES[service]}/{service}"
    if request.query_params:
        target_url += f"?{request.query_params}"

    body = await request.body()
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length")
    }

    logger.info(f"[Gateway] {request.method} /{service}/{path} → {target_url}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
            )
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code,
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"Service '{service}' is not reachable. Is it running on port {SERVICES[service].split(':')[-1]}?"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail=f"Service '{service}' timed out."
        )
    except Exception as e:
        logger.error(f"Gateway error: {e}")
        raise HTTPException(status_code=500, detail="Internal gateway error")
