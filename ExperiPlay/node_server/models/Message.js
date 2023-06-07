const mongoose = require('../utils/database');

// Define the message schema for MongoDB
const messageSchema = new mongoose.Schema({
  role: String,
  content: String,
  createdAt: { type: Date, default: Date.now },
});

// Create a model from the schema
const Message = mongoose.model('Message', messageSchema);

module.exports = Message;
