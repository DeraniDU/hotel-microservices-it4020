const express = require("express");
const dotenv = require("dotenv");
const cors = require("cors");
const connectDB = require("./config/db");
const swaggerUi = require('swagger-ui-express');
const swaggerDocument = require('./swagger.json');

// Load env variables
dotenv.config();

// Connect to database
connectDB();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Sample route
app.get("/", (req, res) => {
<<<<<<< HEAD
  res.redirect("/room");
=======
  res.redirect("/api-docs");
>>>>>>> f9b35c0229d3cb1dbbcbd09725f8abe398ab5ada
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

// Swagger API Documentation
const options = {};
app.get('/api-docs', (req, res, next) => {
    if (!req.originalUrl.endsWith('/')) {
        return res.redirect(301, req.originalUrl + '/');
    }
    next();
});
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument, options));

app.use("/api/rooms", require("./routes/roomRoutes"));

// Port
const PORT = process.env.PORT || 5000;

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

