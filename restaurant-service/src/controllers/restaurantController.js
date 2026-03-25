const menuItems = require('../data/menuData');

// Get all menu items
exports.getAllMenuItems = (req, res) => {
    res.json(menuItems);
};

// Get single menu item by ID
exports.getMenuItemById = (req, res) => {
    const item = menuItems.find(i => i.id === parseInt(req.params.id));
    if (!item) {
        return res.status(404).send({ message: 'Menu item not found' });
    }
    res.json(item);
};

// Add a new menu item
exports.createMenuItem = (req, res) => {
    const { name, description, price, isAvailable } = req.body;
    
    // Simple ID generator
    const newId = menuItems.length > 0 ? Math.max(...menuItems.map(i => i.id)) + 1 : 1;
    
    const newItem = {
        id: newId,
        name,
        description: description || '',
        price: price || 0,
        isAvailable: isAvailable !== undefined ? isAvailable : true
    };
    
    menuItems.push(newItem);
    res.status(201).json(newItem);
};

// Update a menu item
exports.updateMenuItem = (req, res) => {
    const item = menuItems.find(i => i.id === parseInt(req.params.id));
    if (!item) {
        return res.status(404).send({ message: 'Menu item not found' });
    }

    const { name, description, price, isAvailable } = req.body;
    
    if (name !== undefined) item.name = name;
    if (description !== undefined) item.description = description;
    if (price !== undefined) item.price = price;
    if (isAvailable !== undefined) item.isAvailable = isAvailable;

    res.json(item);
};

// Delete a menu item
exports.deleteMenuItem = (req, res) => {
    const itemIndex = menuItems.findIndex(i => i.id === parseInt(req.params.id));
    if (itemIndex === -1) {
        return res.status(404).send({ message: 'Menu item not found' });
    }

    menuItems.splice(itemIndex, 1);
    res.send({ message: 'Menu item deleted successfully' });
};
