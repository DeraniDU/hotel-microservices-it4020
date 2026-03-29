const Room = require("../modules/Room");

const VALID_TYPES = ["Single", "Double", "Suite"];

// Helper: normalize and validate numeric price
function parsePrice(value) {
  if (value === undefined || value === null) return undefined;
  const n = Number(value);
  return Number.isFinite(n) ? n : NaN;
}

// CREATE
exports.createRoom = async (req, res) => {
  try {
    const data = { ...req.body };
    // Prevent client from setting roomNumber
    if (data.roomNumber) delete data.roomNumber;

    if (!data.type || !VALID_TYPES.includes(data.type)) {
      return res.status(400).json({ message: `type is required and must be one of ${VALID_TYPES.join(", ")}` });
    }

    const price = parsePrice(data.price);
    if (price === undefined || isNaN(price) || price < 0) {
      return res.status(400).json({ message: "price is required and must be a non-negative number" });
    }
    data.price = price;

    const room = await Room.create(data);
    res.status(201).json(room);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// READ ALL
exports.getRooms = async (req, res) => {
  const rooms = await Room.find();
  res.json(rooms);
};

// READ ONE
exports.getRoomById = async (req, res) => {
  try {
    const room = await Room.findById(req.params.id);
    if (!room) return res.status(404).json({ message: "Room not found" });

    res.json(room);
  } catch (err) {
    res.status(400).json({ message: "Invalid ID" });
  }
};

// UPDATE
exports.updateRoom = async (req, res) => {
  try {
    const data = { ...req.body };
    // Prevent changing roomNumber
    if (data.roomNumber) delete data.roomNumber;

    if (data.type && !VALID_TYPES.includes(data.type)) {
      return res.status(400).json({ message: `type must be one of ${VALID_TYPES.join(", ")}` });
    }

    if (data.price !== undefined) {
      const price = parsePrice(data.price);
      if (isNaN(price) || price < 0) {
        return res.status(400).json({ message: "price must be a non-negative number" });
      }
      data.price = price;
    }

    const room = await Room.findByIdAndUpdate(req.params.id, data, { new: true, runValidators: true });

    if (!room) return res.status(404).json({ message: "Room not found" });

    res.json(room);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// DELETE
exports.deleteRoom = async (req, res) => {
  try {
    const room = await Room.findByIdAndDelete(req.params.id);

    if (!room) return res.status(404).json({ message: "Room not found" });

    res.json({ message: "Room deleted" });
  } catch (err) {
    res.status(400).json({ message: "Invalid ID" });
  }
};