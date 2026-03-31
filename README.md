#  Hotel Management Microservices
**IT4020 — Modern Topics in IT | Assignment 2 | 2026**

## Team
| Member      | Service            | Branch                    |
|-------------|--------------------|---------------------------|
| Deranindu   | Guest Service , API Gateway + Setup    | feature/guest-service , feature/api-gateway    |
| Rashini     | Room Service       | feature/room-service      |
| Kavindu      | Booking Service    | feature/booking-service   |
| Sadeepa       | Payment Service    | feature/payment-service   |
| Malshan     | Restaurant Service | feature/restaurant-service|
| Raveen      | Staff Service      | feature/staff-service     |

## Running a single service
```bash
cd guest-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## Running Staff Service
```bash
cd staff-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8006
```

## Running the API Gateway
```bash
cd api-gateway
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Ports
| Service        | Port | Swagger UI                      |
|----------------|------|---------------------------------|
| API Gateway    | 8000 | http://localhost:8000/docs      |
| Guest          | 8001 | http://localhost:8001/docs      |
| Room           | 8002 | http://localhost:8002/docs      |
| Booking        | 8003 | http://localhost:8003/docs      |
| Payment        | 8004 | http://localhost:8004/docs      |
| Restaurant     | 8005 | http://localhost:8005/docs      |
| Staff          | 8006 | http://localhost:8006/docs      |


## Running All Services (one-by-one)
Open separate terminals and run these commands in order (one service per terminal):

```bash
# Terminal 1 — API Gateway
cd api-gateway && pip3 install -r requirements.txt && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Guest Service (Python)
cd guest-service && pip3 install -r requirements.txt && python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 3 — Room Service (Node.js)
cd room-service && npm install && npm start

# Terminal 4 — Booking Service (Python)
cd booking-service && pip3 install -r requirements.txt && python3 -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload

# Terminal 5 — Payment Service (Python)
cd payment-service && pip3 install -r requirements.txt && python3 -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload

# Terminal 6 — Restaurant Service (Node.js)
cd restaurant-service && npm install && npm start

# Terminal 7 — Staff Service (Python)
cd staff-service && pip3 install -r requirements.txt && python3 -m uvicorn main:app --host 0.0.0.0 --port 8006 --reload
```
