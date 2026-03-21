# 🏨 Hotel Management Microservices
**IT4020 — Modern Topics in IT | Assignment 2 | 2026**

## Team
| Member      | Service            | Branch                    |
|-------------|--------------------|---------------------------|
| Deranindu   | Guest Service  API Gateway + Setup    | feature/guest-service , feature/api-gateway    |
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
