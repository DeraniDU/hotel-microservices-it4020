const mongoose = require('mongoose');

const MenuSchema = new mongoose.Schema(
  {
    itemId: { type: Number, index: true, unique: false, required: false },
    name: { type: String, required: true },
    description: { type: String, default: '' },
    price: { type: Number, required: true, default: 0 },
    isAvailable: { type: Boolean, default: true },
  },
  { timestamps: true }
);

module.exports = mongoose.model('MenuItem', MenuSchema);
