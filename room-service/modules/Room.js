const mongoose = require("mongoose");

const roomSchema = new mongoose.Schema({
  roomNumber: {
    type: Number,
    required: true,
    unique: true
  },
  type: {
    type: String,
    enum: ["Single", "Double", "Suite"],
    required: true
  },
  price: {
    type: Number,
    required: true
  },
  isAvailable: {
    type: Boolean,
    default: true
  }
});

module.exports = mongoose.model("Room", roomSchema);