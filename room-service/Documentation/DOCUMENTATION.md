# Room Service Documentation

## Project Overview

This microservice manages hotel rooms: creation, retrieval, update, and deletion. It exposes a JSON REST API under the `/api/rooms` path and uses MongoDB via Mongoose.

Repository: room-service

## Files & Purpose

- server.js: App entry, middleware, route registration, DB connect.
- config/db.js: MongoDB connection helper (reads `process.env.MONGO_URI`).
- routes/roomRoutes.js: Express routes mapping HTTP methods and paths to controller functions.
- controllers/roomController.js: Request handlers and validation logic for the Room endpoints.
- modules/Room.js: Mongoose schema and model for `Room`. Also contains a `Counter` model to auto-generate `roomNumber` values.
- package.json: Project metadata and start script.

Path: [room-service/Documentation/DOCUMENTATION.md](room-service/Documentation/DOCUMENTATION.md)

## Setup & Run

1. Create a `.env` file in `room-service` with at least:

```
MONGO_URI=mongodb://<host>:<port>/<db>
PORT=5000
```

2. Install dependencies:

```bash
cd room-service
npm install
```

3. Start the service:

```bash
npm start
```

Server default route: `GET /` → responds with "API is running...".

## Database

- MongoDB is required and the connection string must be set in `MONGO_URI`.
- The `modules/Room.js` file defines a small `Counter` collection used to track a sequence (`id: 'room'`) and generate `roomNumber` as `RM_XXX`.

Notes on `roomNumber` generation:
- On document validation, if a new Room has no `roomNumber`, the pre-validate hook increments the `Counter` sequence and assigns `RM_<zero-padded seq>` (e.g., `RM_001`, `RM_012`).
- This approach is simple and works for many cases; for high concurrency or multi-instance deployments consider transactions or a dedicated sequence service.

## API Endpoints (routes/roomRoutes.js)

Base: `/api/rooms`

- POST `/addroom` — Create a room
  - Controller: `createRoom()` in `controllers/roomController.js`
  - Request body (JSON):
    - `type` (required): one of `Single`, `Double`, `Suite`
    - `price` (required): non-negative number
    - `isAvailable` (optional): boolean
  - Notes: `roomNumber` is auto-generated; any client-supplied `roomNumber` is ignored.
  - Success: 201 Created — returns created room object
  - Errors: 400 Bad Request — validation errors

- GET `/getrooms` — Get all rooms
  - Controller: `getRooms()`
  - Success: 200 OK — array of room objects

- GET `/getsingleroom/:id` — Get a single room by MongoDB `_id`
  - Controller: `getRoomById()`
  - Success: 200 OK — room object
  - Errors: 404 Not Found, 400 Invalid ID

- PUT `/updateroom/:id` — Update a room by `_id`
  - Controller: `updateRoom()`
  - Request body: any of `type`, `price`, `isAvailable`.
  - Notes: `roomNumber` cannot be updated by clients.
  - Success: 200 OK — updated room
  - Errors: 400 Bad Request, 404 Not Found

- DELETE `/droproom/:id` — Delete a room by `_id`
  - Controller: `deleteRoom()`
  - Success: 200 OK — JSON message `Room deleted`

## Controller Details (controllers/roomController.js)

All exported functions are async express handlers:

- `createRoom(req, res)`
  - Validations:
    - `type` must exist and be one of `Single|Double|Suite` (uses `VALID_TYPES`).
    - `price` must be present, numeric, and >= 0 (helper `parsePrice`).
    - Removes any `roomNumber` from client payload so the server generates it.
  - Behavior: calls `Room.create(data)` (Mongoose). On success returns 201 and the created doc.

- `getRooms(req, res)`
  - Behavior: `Room.find()` and returns the array.

- `getRoomById(req, res)`
  - Behavior: `Room.findById(req.params.id)`; returns 404 if not found; 400 for invalid id.

- `updateRoom(req, res)`
  - Validations:
    - Strips any `roomNumber` from body.
    - If `type` present, must be one of `VALID_TYPES`.
    - If `price` present, it must be numeric and >= 0.
  - Behavior: `Room.findByIdAndUpdate(id, data, { new: true, runValidators: true })`.

- `deleteRoom(req, res)`
  - Behavior: `Room.findByIdAndDelete(id)`; 404 if not found.

## Model Details (modules/Room.js)

Schema: `roomSchema`

- `roomNumber` (String, required, unique)
  - Generated automatically as `RM_XXX` via pre-validate hook using `Counter`.
- `type` (String, enum: `Single|Double|Suite`, required)
- `price` (Number, required, min 0)
- `isAvailable` (Boolean, default true)

Counter model (`Counter`) stores documents like `{ id: 'room', seq: 12 }`. The code uses `findOneAndUpdate({ id: 'room' }, { $inc: { seq: 1 } }, { new: true, upsert: true })`.

## Error Handling

- Controller functions return 400 for validation errors and 404 when resources do not exist.
- `connectDB()` exits the process on MongoDB connection error.

## Example Requests

Create a room:

```bash
curl -X POST http://localhost:5000/api/rooms/addroom \
  -H "Content-Type: application/json" \
  -d '{"type":"Double","price":120}'
```

Response (example):

```json
{
  "_id": "642...",
  "roomNumber": "RM_001",
  "type": "Double",
  "price": 120,
  "isAvailable": true,
  "__v": 0
}
```

Get all rooms:

```bash
curl http://localhost:5000/api/rooms/getrooms
```

Update a room:

```bash
curl -X PUT http://localhost:5000/api/rooms/updateroom/:id \
  -H "Content-Type: application/json" \
  -d '{"price":150,"isAvailable":false}'
```

Delete a room:

```bash
curl -X DELETE http://localhost:5000/api/rooms/droproom/:id
```
