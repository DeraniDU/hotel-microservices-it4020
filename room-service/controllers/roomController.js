const Room = require("../modules/Room");

// CREATE
exports.createRoom = async (req, res) => {
  try {
    const room = await Room.create(req.body);
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
  } catch {
    res.status(400).json({ message: "Invalid ID" });
  }
};

// UPDATE
exports.updateRoom = async (req, res) => {
  try {
    const room = await Room.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );

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
  } catch {
    res.status(400).json({ message: "Invalid ID" });
  }
};