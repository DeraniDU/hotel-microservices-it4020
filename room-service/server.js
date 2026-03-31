const express = require("express");
const dotenv = require("dotenv");
const cors = require("cors");
const connectDB = require("./config/db");

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
  res.send("API is running...");
});

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

