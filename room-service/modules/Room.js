const mongoose = require("mongoose");

const counterSchema = new mongoose.Schema({
  id: { type: String, required: true, unique: true },
  seq: { type: Number, default: 0 }
});

const Counter = mongoose.model("Counter", counterSchema);

const roomSchema = new mongoose.Schema({
  roomNumber: {
    type: String,
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
    required: true,
    min: 0
  },
  isAvailable: {
    type: Boolean,
    default: true
  }
});

roomSchema.pre("validate", async function () {
  if (this.isNew && !this.roomNumber) {
    const counter = await Counter.findOneAndUpdate(
      { id: "room" },
      { $inc: { seq: 1 } },
      { new: true, upsert: true }
    );

    const seq = counter.seq || 1;
    this.roomNumber = `RM_${String(seq).padStart(3, "0")}`;
  }
});

module.exports = mongoose.model("Room", roomSchema);