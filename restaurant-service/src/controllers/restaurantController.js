const Menu = require('../models/Menu');

// Get all menu items
exports.getAllMenuItems = async (req, res) => {
    try {
        const items = await Menu.find().sort({ createdAt: -1 }).lean();
        return res.json(items);
    } catch (err) {
        console.error(err);
        return res.status(500).json({ message: 'Server error' });
    }
};

// Get single menu item by ID (tries numeric itemId first, then Mongo _id)
exports.getMenuItemById = async (req, res) => {
    try {
        const param = req.params.id;
        let item = null;
        if (!isNaN(Number(param))) {
            item = await Menu.findOne({ itemId: Number(param) }).lean();
        }
        if (!item) {
            item = await Menu.findById(param).lean().catch(() => null);
        }
        if (!item) return res.status(404).send({ message: 'Menu item not found' });
        return res.json(item);
    } catch (err) {
        console.error(err);
        return res.status(500).json({ message: 'Server error' });
    }
};

// Add a new menu item
exports.createMenuItem = async (req, res) => {
    try {
        const { name, description, price, isAvailable, id } = req.body;
        // Determine itemId if provided or assign auto increment based on max itemId
        let itemId = undefined;
        if (id !== undefined) itemId = Number(id);
        else {
            const last = await Menu.findOne().sort({ itemId: -1 }).lean();
            itemId = last && last.itemId ? last.itemId + 1 : 1;
        }

        const newItem = new Menu({
            itemId,
            name,
            description: description || '',
            price: price || 0,
            isAvailable: isAvailable !== undefined ? isAvailable : true,
        });

        const saved = await newItem.save();
        return res.status(201).json(saved);
    } catch (err) {
        console.error(err);
        return res.status(500).json({ message: 'Server error' });
    }
};

// Update a menu item
exports.updateMenuItem = async (req, res) => {
    try {
        const param = req.params.id;
        let query = {};
        if (!isNaN(Number(param))) query = { itemId: Number(param) };
        else query = { _id: param };

        const update = req.body;
        const updated = await Menu.findOneAndUpdate(query, update, { returnDocument: 'after' }).lean();
        if (!updated) return res.status(404).json({ message: 'Menu item not found' });
        return res.json(updated);
    } catch (err) {
        console.error(err);
        return res.status(500).json({ message: 'Server error' });
    }
};

// Delete a menu item
exports.deleteMenuItem = async (req, res) => {
    try {
        const param = req.params.id;
        let query = {};
        if (!isNaN(Number(param))) query = { itemId: Number(param) };
        else query = { _id: param };

        const deleted = await Menu.findOneAndDelete(query).lean();
        if (!deleted) return res.status(404).json({ message: 'Menu item not found' });
        return res.json({ message: 'Menu item deleted successfully' });
    } catch (err) {
        console.error(err);
        return res.status(500).json({ message: 'Server error' });
    }
};
