const express = require("express");
const router = express.Router();

const {
  createRoom,
  getRooms,
  getRoomById,
  updateRoom,
  deleteRoom
} = require("../controllers/roomController");

router.post("/addroom", createRoom);
router.get("/getrooms", getRooms);
router.get("/getsingleroom/:id", getRoomById);
router.put("/updateroom/:id", updateRoom);
router.delete("/droproom/:id", deleteRoom);

module.exports = router;