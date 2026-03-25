const express = require('express');
const cors = require('cors');
const swaggerUi = require('swagger-ui-express');
const swaggerDocument = require('./swagger.json');
const restaurantRoutes = require('./src/routes/restaurantRoutes');

const app = express();
const PORT = process.env.PORT || 8005;

// Middleware
app.use(cors());
app.use(express.json());

// Main Root Endpoint
app.get('/', (req, res) => {
    res.send('Restaurant Microservice is working! Use Postman to hit /api/restaurant/menu');
});

// Health Endpoint — required for API Gateway
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'online', service: 'restaurant-service' });
});

// Swagger API Documentation Route
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

// Restaurant API Routes
app.use('/api/restaurant', restaurantRoutes);

// Start Server
app.listen(PORT, () => {
    console.log(`Server is successfully running on port ${PORT}`);
    console.log(`API Documentation is at http://localhost:${PORT}/api-docs`);
    console.log(`Health check at http://localhost:${PORT}/health`);
});