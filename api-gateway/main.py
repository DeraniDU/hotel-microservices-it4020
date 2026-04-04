from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api-gateway")

# ── Service Registry ───────────────────────────────────────────────────────────
SERVICES = {
    "guests": {
        "display_name": "Guest Service",
        "description": "Manages hotel guests — check-in, check-out, profiles",
        "port": 8001,
        "url": "http://localhost:8001",
        "language": "Python",
        "framework": "FastAPI",
        "db": "MongoDB",
        "color": "#6366f1",
        "icon": "👤",
        "start_cmd": "cd guest-service && python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload",
        "docs_url": "/docs",
    },
    "rooms": {
        "display_name": "Room Service",
        "description": "Manages hotel rooms — availability, types, pricing",
        "port": 8002,
        "url": "http://localhost:8002",
        "language": "Node.js",
        "framework": "Express",
        "db": "MongoDB",
        "color": "#10b981",
        "icon": "🛏️",
        "start_cmd": "cd room-service && npm start",
        "docs_url": "/api-docs",
    },
    "bookings": {
        "display_name": "Booking Service",
        "description": "Handles reservations, date conflicts, booking IDs",
        "port": 8003,
        "url": "http://localhost:8003",
        "language": "Python",
        "framework": "FastAPI",
        "db": "MongoDB",
        "color": "#f59e0b",
        "icon": "📅",
        "start_cmd": "cd booking-service && python3 -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload",
        "docs_url": "/docs",
    },
    "payments": {
        "display_name": "Payment Service",
        "description": "Processes payments, refunds, and billing records",
        "port": 8004,
        "url": "http://localhost:8004",
        "language": "Python",
        "framework": "FastAPI",
        "db": "MongoDB",
        "color": "#ec4899",
        "icon": "💳",
        "start_cmd": "cd payment-service && python3 -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload",
        "docs_url": "/payment",
    },
    "restaurant": {
        "display_name": "Restaurant Service",
        "description": "Manages menu, orders, and restaurant reservations",
        "port": 8005,
        "url": "http://localhost:8005",
        "language": "Node.js",
        "framework": "Express",
        "db": "MongoDB",
        "color": "#f97316",
        "icon": "🍽️",
        "start_cmd": "cd restaurant-service && npm start",
        "docs_url": "/api-docs",
    },
    "staff": {
        "display_name": "Staff Service",
        "description": "Manages employee records, roles, and departments",
        "port": 8006,
        "url": "http://localhost:8006",
        "language": "Python",
        "framework": "FastAPI",
        "db": "MongoDB",
        "color": "#8b5cf6",
        "icon": "👷",
        "start_cmd": "cd staff-service && python3 -m uvicorn main:app --host 0.0.0.0 --port 8006 --reload",
        "docs_url": "/staff",
    },
}

# Public gateway path segment (may differ from registry key, e.g. staff → /staffs).
def gateway_path_for_service(service_key: str) -> str:
    if service_key == "staff":
        return "staffs"
    return service_key


# ── App ────────────────────────────────────────────────────────────────────────
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
| Staff       | /staffs/...      | 8006        |
""",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Dashboard HTML ─────────────────────────────────────────────────────────────
def build_dashboard_html() -> str:
    service_cards = ""
    docs_routes = {
        "guests": "guest",
        "rooms": "room",
        "bookings": "booking",
        "payments": "payment",
        "restaurant": "restaurant",
        "staff": "staff"
    }
    
    for key, svc in SERVICES.items():
        framework_badge = f'<span class="badge badge-framework">{svc["framework"]}</span>'
        lang_badge = f'<span class="badge badge-lang">{svc["language"]}</span>'
        db_badge = f'<span class="badge badge-db">{svc["db"]}</span>'
        docs_route = docs_routes.get(key, 'docs')
        docs_url = f"{svc['url']}{svc.get('docs_url', '/' + docs_route)}"
        if key == "staff":
            gateway_route = f"http://localhost:8000/{gateway_path_for_service(key)}"
        elif svc["framework"] == "Express":
            gateway_route = f"http://localhost:8000/api/{docs_route}/"
        else:
            gateway_route = f"http://localhost:8000/api/{docs_route}"
        service_cards += f"""
        <div class="service-card" id="card-{key}" data-service="{key}">
            <div class="card-header" style="border-top:3px solid {svc['color']}">
                <div class="card-title-row">
                    <span class="service-icon">{svc['icon']}</span>
                    <div>
                        <h3 class="service-name">{svc['display_name']}</h3>
                        <span class="service-url">localhost:{svc['port']}/{gateway_path_for_service(key)}</span>
                    </div>
                    <span class="status-badge" id="status-{key}">
                        <span class="status-dot" id="dot-{key}"></span>
                        <span id="status-text-{key}">checking…</span>
                    </span>
                </div>
                <p class="service-desc">{svc['description']}</p>
                <div class="badge-row">
                    {lang_badge}{framework_badge}{db_badge}
                </div>
            </div>
            <div class="card-body">
                <div class="cmd-block">
                    <span class="cmd-label">▶ Start</span>
                    <code class="cmd-text" id="cmd-{key}">{svc['start_cmd']}</code>
                    <button class="copy-btn" onclick="copyCmd('{key}')">Copy</button>
                </div>
                <div class="card-actions">
                    <a href="{gateway_route}" target="_blank" class="btn btn-primary" style="background:{svc['color']}">Open via Gateway</a>
                    <a href="{docs_url}" target="_blank" class="btn btn-outline">📄 Docs</a>
                </div>
            </div>
        </div>
"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>🏨 Hotel Microservices — API Gateway</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2236;
    --border: #1f2d45;
    --text: #e2e8f0;
    --muted: #64748b;
    --accent: #6366f1;
  }}
  body {{
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }}

  /* ── Header ── */
  header {{
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border-bottom: 1px solid var(--border);
    padding: 0 2rem;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(12px);
  }}
  .header-inner {{
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 72px;
  }}
  .logo {{ display: flex; align-items: center; gap: 12px; }}
  .logo-icon {{
    width: 42px; height: 42px; border-radius: 10px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
  }}
  .logo-text h1 {{ font-size: 18px; font-weight: 700; }}
  .logo-text p {{ font-size: 12px; color: var(--muted); }}
  .header-right {{ display: flex; align-items: center; gap: 12px; }}
  .gateway-badge {{
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.35);
    color: #a5b4fc;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
  }}
  .refresh-indicator {{
    display: flex; align-items: center; gap: 6px;
    color: var(--muted); font-size: 12px;
  }}
  .pulse-ring {{
    width: 8px; height: 8px; border-radius: 50%;
    background: #10b981;
    animation: pulse-ring 2s ease-in-out infinite;
  }}
  @keyframes pulse-ring {{
    0%, 100% {{ opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }}
    50%        {{ opacity: 0.8; transform: scale(1.15); box-shadow: 0 0 0 6px rgba(16,185,129,0); }}
  }}

  /* ── Hero ── */
  .hero {{
    max-width: 1400px;
    margin: 0 auto;
    padding: 3rem 2rem 2rem;
  }}
  .hero-title {{
    font-size: clamp(28px, 4vw, 42px);
    font-weight: 800;
    background: linear-gradient(135deg, #e2e8f0, #a5b4fc 60%, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 10px;
  }}
  .hero-sub {{ color: var(--muted); font-size: 15px; margin-bottom: 2rem; }}
  .stats-row {{ display: flex; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 2.5rem; }}
  .stat-pill {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 10px 18px;
    display: flex; align-items: center; gap: 8px;
    font-size: 13px;
  }}
  .stat-num {{ font-weight: 700; font-size: 18px; color: #a5b4fc; }}

  /* ── Section title ── */
  .section-title {{
    font-size: 11px; font-weight: 600; letter-spacing: 1.5px;
    text-transform: uppercase; color: var(--muted);
    margin-bottom: 1rem;
    display: flex; align-items: center; gap: 8px;
  }}
  .section-title::after {{
    content: ''; flex: 1; height: 1px;
    background: var(--border);
  }}

  /* ── Grid ── */
  .services-grid {{
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 2rem 3rem;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 1.25rem;
  }}

  /* ── Service Card ── */
  .service-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    cursor: default;
  }}
  .service-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    border-color: rgba(99,102,241,0.3);
  }}
  .card-header {{ padding: 1.25rem 1.25rem 0.75rem; }}
  .card-title-row {{
    display: flex; align-items: flex-start; gap: 12px;
    margin-bottom: 0.75rem;
  }}
  .service-icon {{
    font-size: 28px;
    width: 48px; height: 48px;
    background: var(--surface2);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }}
  .service-name {{ font-size: 16px; font-weight: 700; margin-bottom: 2px; }}
  .service-url {{ font-size: 11px; color: var(--muted); font-family: 'Courier New', monospace; }}
  .service-desc {{ font-size: 13px; color: var(--muted); line-height: 1.5; margin-bottom: 0.75rem; }}
  .badge-row {{ display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 0.25rem; }}
  .badge {{
    font-size: 11px; font-weight: 500;
    padding: 3px 9px; border-radius: 20px;
    border: 1px solid;
  }}
  .badge-lang {{
    color: #93c5fd; background: rgba(59,130,246,0.12);
    border-color: rgba(59,130,246,0.25);
  }}
  .badge-framework {{
    color: #6ee7b7; background: rgba(16,185,129,0.12);
    border-color: rgba(16,185,129,0.25);
  }}
  .badge-db {{
    color: #fca5a5; background: rgba(239,68,68,0.12);
    border-color: rgba(239,68,68,0.25);
  }}

  /* ── Status Badge ── */
  .status-badge {{
    margin-left: auto;
    display: flex; align-items: center; gap: 5px;
    font-size: 11px; font-weight: 600;
    padding: 4px 10px; border-radius: 20px;
    background: var(--surface2);
    border: 1px solid var(--border);
    white-space: nowrap; flex-shrink: 0;
    transition: all 0.3s ease;
  }}
  .status-dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--muted);
    transition: background 0.3s ease;
  }}
  .status-online   .status-dot {{ background: #10b981; box-shadow: 0 0 6px #10b981; animation: dot-pulse 2s infinite; }}
  .status-offline  .status-dot {{ background: #ef4444; }}
  .status-degraded .status-dot {{ background: #f59e0b; }}
  @keyframes dot-pulse {{
    0%, 100% {{ box-shadow: 0 0 0 0 rgba(16,185,129,0.5); }}
    50%        {{ box-shadow: 0 0 0 5px rgba(16,185,129,0); }}
  }}
  .status-online  {{ border-color: rgba(16,185,129,0.3); color: #34d399; }}
  .status-offline {{ border-color: rgba(239,68,68,0.3);  color: #f87171; }}
  .status-degraded {{ border-color: rgba(245,158,11,0.3); color: #fbbf24; }}

  /* ── Card Body ── */
  .card-body {{
    padding: 0.75rem 1.25rem 1.25rem;
    border-top: 1px solid var(--border);
  }}
  .cmd-block {{
    background: #0d111b;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 0.85rem;
    display: flex;
    align-items: center;
    gap: 8px;
    overflow: hidden;
  }}
  .cmd-label {{
    font-size: 10px; font-weight: 600; letter-spacing: 0.5px;
    color: #10b981; flex-shrink: 0;
  }}
  .cmd-text {{
    font-family: 'Courier New', monospace;
    font-size: 11px; color: #94a3b8;
    flex: 1; overflow: hidden;
    text-overflow: ellipsis; white-space: nowrap;
  }}
  .copy-btn {{
    background: var(--surface2); border: 1px solid var(--border);
    color: var(--muted); font-size: 11px; padding: 3px 8px;
    border-radius: 6px; cursor: pointer; flex-shrink: 0;
    transition: all 0.15s ease;
  }}
  .copy-btn:hover {{ color: var(--text); border-color: rgba(99,102,241,0.5); }}
  .card-actions {{ display: flex; gap: 8px; }}
  .btn {{
    flex: 1; text-align: center; padding: 9px 14px;
    border-radius: 9px; font-size: 13px; font-weight: 600;
    text-decoration: none; transition: all 0.2s ease;
    border: none; cursor: pointer;
  }}
  .btn-primary {{ color: #fff; opacity: 0.92; }}
  .btn-primary:hover {{ opacity: 1; transform: scale(1.02); }}
  .btn-outline {{
    background: var(--surface2); color: var(--muted);
    border: 1px solid var(--border);
  }}
  .btn-outline:hover {{ color: var(--text); border-color: rgba(99,102,241,0.4); }}

  /* ── Gateway Info Box ── */
  .gateway-info {{
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 2rem 2rem;
  }}
  .info-box {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1rem;
  }}
  .info-item {{ display: flex; flex-direction: column; gap: 4px; }}
  .info-label {{ font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }}
  .info-value {{ font-size: 14px; font-weight: 600; font-family: 'Courier New', monospace; color: #a5b4fc; }}

  /* ── Footer ── */
  footer {{
    text-align: center;
    padding: 1.5rem;
    color: var(--muted);
    font-size: 12px;
    border-top: 1px solid var(--border);
  }}
  footer a {{ color: #6366f1; text-decoration: none; }}
</style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="logo">
      <div class="logo-icon">🏨</div>
      <div class="logo-text">
        <h1>Hotel Microservices</h1>
        <p>API Gateway Dashboard</p>
      </div>
    </div>
    <div class="header-right">
      <span class="gateway-badge">📡 localhost:8000</span>
      <div class="refresh-indicator">
        <div class="pulse-ring"></div>
        <span id="last-check">Live</span>
      </div>
    </div>
  </div>
</header>

<div class="hero">
  <h2 class="hero-title">Microservices Control Center</h2>
  <p class="hero-sub">All services route through the API Gateway on port 8000. Monitor health, open docs, and copy start commands below.</p>
  <div class="stats-row">
    <div class="stat-pill"><span class="stat-num">6</span> Microservices</div>
    <div class="stat-pill"><span class="stat-num" id="online-count">—</span> Online</div>
    <div class="stat-pill"><span class="stat-num">8000</span> Gateway Port</div>
    <div class="stat-pill"><span class="stat-num">v2.0</span> Gateway Version</div>
  </div>
  <p class="section-title">Services</p>
</div>

<div class="services-grid">
{service_cards}
</div>

<div class="gateway-info">
  <p class="section-title" style="margin-bottom:1rem">Gateway Endpoints</p>
  <div class="info-box">
    <div class="info-item">
      <span class="info-label">Gateway Dashboard</span>
      <span class="info-value">GET http://localhost:8000/</span>
    </div>
    <div class="info-item">
      <span class="info-label">Gateway Info (JSON)</span>
      <span class="info-value">GET http://localhost:8000/api-gateway</span>
    </div>
    <div class="info-item">
      <span class="info-label">Services List (JSON)</span>
      <span class="info-value">GET http://localhost:8000/api-gateway/services</span>
    </div>
    <div class="info-item">
      <span class="info-label">Health Check</span>
      <span class="info-value">GET http://localhost:8000/health</span>
    </div>
    <div class="info-item">
      <span class="info-label">Proxy Any Service</span>
      <span class="info-value">http://localhost:8000/{{"{{"}}service{{"}}"}}/...</span>
    </div>
    <div class="info-item">
      <span class="info-label">Staff Service API (via gateway)</span>
      <span class="info-value">http://localhost:8000/staffs</span>
    </div>
    <div class="info-item">
      <span class="info-label">API Gateway Docs</span>
      <span class="info-value"><a href="/docs" style="color:#818cf8">http://localhost:8000/docs</a></span>
    </div>
  </div>
</div>

<footer>
  &copy; 2026 Hotel Microservices — Group 63 &nbsp;·&nbsp;
  <a href="/docs">Swagger UI</a> &nbsp;·&nbsp;
  <a href="/api-gateway">Gateway API</a>
</footer>

<script>
  const SERVICES = {list(SERVICES.keys())};

  function setStatus(key, status) {{
    const badge = document.getElementById('status-' + key);
    const dot   = document.getElementById('dot-' + key);
    const txt   = document.getElementById('status-text-' + key);
    badge.className = 'status-badge status-' + status;
    txt.textContent = status === 'online' ? 'Online' : status === 'offline' ? 'Offline' : status.charAt(0).toUpperCase() + status.slice(1);
  }}

  async function pollHealth() {{
    try {{
      const res = await fetch('/health');
      const data = await res.json();
      let onlineCount = 0;
      for (const [key, status] of Object.entries(data.services || {{}})) {{
        setStatus(key, status);
        if (status === 'online') onlineCount++;
      }}
      document.getElementById('online-count').textContent = onlineCount;
      document.getElementById('last-check').textContent = 'Updated ' + new Date().toLocaleTimeString();
    }} catch(e) {{
      console.warn('Health check failed', e);
    }}
  }}

  function copyCmd(key) {{
    const text = document.getElementById('cmd-' + key).textContent;
    navigator.clipboard.writeText(text).then(() => {{
      const btn = event.target;
      btn.textContent = 'Copied!';
      btn.style.color = '#34d399';
      setTimeout(() => {{ btn.textContent = 'Copy'; btn.style.color = ''; }}, 2000);
    }});
  }}

  // Initial poll + repeat every 5 seconds
  pollHealth();
  setInterval(pollHealth, 5000);
</script>
</body>
</html>"""


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, tags=["Dashboard"], include_in_schema=False)
async def dashboard():
    """Returns the interactive HTML dashboard for the API Gateway."""
    return HTMLResponse(content=build_dashboard_html())


@app.get("/api-gateway", tags=["Gateway"])
def gateway_info():
    """Named gateway endpoint — returns gateway metadata and service directory."""
    return {
        "name": "Hotel Management API Gateway",
        "version": "2.0.0",
        "port": 8000,
        "gateway_url": "http://localhost:8000",
        "dashboard": "http://localhost:8000/",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/health",
        "services": {
            key: {
                "display_name": svc["display_name"],
                "gateway_url": f"http://localhost:8000/{gateway_path_for_service(key)}",
                "direct_url": svc["url"],
                "port": svc["port"],
            }
            for key, svc in SERVICES.items()
        },
    }


@app.get("/api-gateway/services", tags=["Gateway"])
def list_services():
    """Returns full metadata for all registered microservices."""
    return [
        {
            "key": key,
            "display_name": svc["display_name"],
            "description": svc["description"],
            "port": svc["port"],
            "direct_url": svc["url"],
            "gateway_url": f"http://localhost:8000/{gateway_path_for_service(key)}",
            "language": svc["language"],
            "framework": svc["framework"],
            "db": svc["db"],
            "start_cmd": svc["start_cmd"],
        }
        for key, svc in SERVICES.items()
    ]


@app.get("/health", tags=["Gateway"])
async def health_check():
    """Check which services are online."""
    status = {}
    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, svc in SERVICES.items():
            try:
                r = await client.get(f"{svc['url']}/health")
                status[name] = "online" if r.status_code == 200 else "degraded"
            except Exception:
                status[name] = "offline"
    return {"gateway": "online", "services": status}


@app.api_route(
    "/{service}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Proxy"],
    summary="Legacy route for microservice root",
)
@app.api_route(
    "/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Proxy"],
    summary="Legacy route for microservice assets",
)
@app.api_route(
    "/api/{service}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Proxy"],
    summary="Route request to the appropriate microservice root",
)
@app.api_route(
    "/api/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Proxy"],
    summary="Route request to the appropriate microservice",
)
async def proxy(service: str, request: Request, path: str = ""):
    ALIAS_ROUTES = {
        "guest": "guests",
        "room": "rooms",
        "booking": "bookings",
        "payment": "payments",
        "staffs": "staff"
    }
    real_service = ALIAS_ROUTES.get(service, service)

    if real_service not in SERVICES:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service}' not found. Available: {list(SERVICES.keys())}"
        )

    svc_url = SERVICES[real_service]["url"]
    
    # We construct the target URL by stripping the "/api" prefix
    incoming_path = request.url.path  
    target_path = incoming_path[4:] if incoming_path.startswith("/api") else incoming_path
    
    target_url = f"{svc_url}{target_path}"
    
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
            # We must override redirect-following so we can return 301/302 to the browser
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
                follow_redirects=False,
            )
            
        from fastapi import Response
        res_headers = dict(response.headers)
        res_headers.pop("content-encoding", None)
        res_headers.pop("content-length", None)
        
        if response.status_code in (301, 302, 303, 307, 308) and "location" in res_headers:
            loc = res_headers["location"]
            if incoming_path.startswith("/api/") and loc.startswith(f"/{service}/"):
                res_headers["location"] = f"/api{loc}"
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=res_headers
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"Service '{service}' is not reachable. Is it running on port {SERVICES[real_service]['port']}?"
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail=f"Service '{service}' timed out.")
    except Exception as e:
        logger.error(f"Gateway error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal gateway error: {str(e)}")
