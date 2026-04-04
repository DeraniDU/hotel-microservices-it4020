const path = require("path");
const express = require("express");
const dotenv = require("dotenv");
const cors = require("cors");
const connectDB = require("./config/db");
const swaggerUi = require('swagger-ui-express');
const swaggerDocument = require('./swagger.json');

dotenv.config({ path: path.join(__dirname, ".env") });
dotenv.config({ path: path.join(__dirname, ".env_room"), override: true });

// Connect to database
connectDB();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Sample route
app.get("/", (req, res) => {
  res.redirect("/room");
});

app.get("/rooms", (req, res) => {
  res.redirect("/room");
});

// Swagger API Documentation Route
app.get('/room', (req, res, next) => {
    if (!req.originalUrl.endsWith('/')) {
        return res.redirect(301, req.originalUrl + '/');
    }
    next();
});
app.use('/room', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

// Health Endpoint - required for API Gateway
app.get("/health", (req, res) => {
  res.status(200).json({ status: "online", service: "room-service" });
});

app.use("/api/rooms", require("./routes/roomRoutes"));

// Port
const PORT = process.env.PORT || 5000;

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

