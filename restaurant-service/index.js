const express = require('express');
const cors = require('cors');
const swaggerUi = require('swagger-ui-express');
const swaggerDocument = require('./swagger.json');
const restaurantRoutes = require('./src/routes/restaurantRoutes');
const dotenv = require('dotenv');
const mongoose = require('mongoose');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8005;

// Middleware
app.use(cors());
app.use(express.json());

// Connect to MongoDB
const connectMongo = async () => {
    try {
        const mongoUrl = process.env.MONGO_URL;
        const dbName = process.env.DATABASE_NAME;
        let connStr = mongoUrl;
        if (mongoUrl && dbName) {
            if (mongoUrl.includes('/?')) connStr = mongoUrl.replace('/?', `/${dbName}?`);
            else if (mongoUrl.endsWith('/')) connStr = `${mongoUrl}${dbName}`;
            else connStr = `${mongoUrl}/${dbName}`;
        }
        await mongoose.connect(connStr, { useNewUrlParser: true, useUnifiedTopology: true });
        console.log('MongoDB connected for restaurant-service');
    } catch (err) {
        console.error('MongoDB connection error (restaurant-service):', err.message);
    }
};
connectMongo();

// Main Root Endpoint
app.get('/', (req, res) => {
<<<<<<< HEAD
    res.redirect('/restaurant');
=======
    res.redirect('/api-docs');
>>>>>>> f9b35c0229d3cb1dbbcbd09725f8abe398ab5ada
});

// Health Endpoint — required for API Gateway
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'online', service: 'restaurant-service' });
});

// Swagger API Documentation Route
<<<<<<< HEAD
app.get('/restaurant', (req, res, next) => {
=======
app.get('/api-docs', (req, res, next) => {
>>>>>>> f9b35c0229d3cb1dbbcbd09725f8abe398ab5ada
    if (!req.originalUrl.endsWith('/')) {
        return res.redirect(301, req.originalUrl + '/');
    }
    next();
});
<<<<<<< HEAD
app.use('/restaurant', swaggerUi.serve, swaggerUi.setup(swaggerDocument));
=======
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));
>>>>>>> f9b35c0229d3cb1dbbcbd09725f8abe398ab5ada

// Restaurant API Routes
app.use('/api/restaurant', restaurantRoutes);

// Start Server
app.listen(PORT, () => {
    console.log(`Server is successfully running on port ${PORT}`);
    console.log(`API Documentation is at http://localhost:${PORT}/api-docs`);
    console.log(`Health check at http://localhost:${PORT}/health`);
});