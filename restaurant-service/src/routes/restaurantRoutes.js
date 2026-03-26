const express = require('express');
const router = express.Router();
const restaurantController = require('../controllers/restaurantController');

// Define routes and attach controller functions
router.get('/menu', restaurantController.getAllMenuItems);
router.get('/menu/:id', restaurantController.getMenuItemById);
router.post('/menu', restaurantController.createMenuItem);
router.put('/menu/:id', restaurantController.updateMenuItem);
router.delete('/menu/:id', restaurantController.deleteMenuItem);

module.exports = router;
