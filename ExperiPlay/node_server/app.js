require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const { getOpenAIChatCompletion, streamTo } = require('./openaiHandler');
require('./utils/database'); // This will connect to MongoDB

const Message = require('./models/Message'); // import our Message model

const app = express();

console.log("Express app created.");

// Setup the view engine, body parser, and static file serving
app.set('view engine', 'ejs');
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(__dirname + '/public'));

console.log("Middleware setup completed.");

// Define the GET route for the home page
app.get('/', (req, res) => {
    res.render('index');
});

console.log("GET route for home page defined.");

// Initialize the chat history
let chatHistory = [];

// Define the POST route for /chat
app.post('/chat', async (req, res) => {
  try {
    const userInput = req.body.userInput;

    // Save the user message to the MongoDB database
    const userMessage = new Message({ role: 'user', content: userInput });
    await userMessage.save();

    console.log("User message saved to database.");

    // Add the user's message to the chat history
    chatHistory.push({role: 'user', content: userInput});

    // Only use the last 5 messages from the chat history
    const recentMessages = chatHistory.slice(-5);

    // Get a chat completion from OpenAI
    getOpenAIChatCompletion(recentMessages)
      .then(async aiResponse => {
        // Save the AI's response to the MongoDB database
        const aiMessage = new Message({ role: 'assistant', content: aiResponse });
        await aiMessage.save();

        console.log("AI message saved to database.");

        // Add the AI's response to the chat history
        chatHistory.push({role: 'assistant', content: aiResponse});

        // Send JSON response after AI's response is received
        res.json({ userMessage: userInput, response: aiResponse });
      })
      .catch(err => {
        console.error("Error occurred while getting chat completion: ", err);
        // Send error status and message
        res.status(500).json({ error: 'An error occurred while processing your request.' });
      });

    // Start a server-sent event
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    console.log("Server-sent event started.");

    // Get and stream the chat completion
    getAndStreamOpenAIChatCompletion(userInput, res);
  } catch (err) {
    console.error("Error occurred in POST /chat: ", err);
    res.status(500).json({ error: 'An error occurred while processing your request.' });
  }
});

async function getAndStreamOpenAIChatCompletion(userInput, res) {
  try {
    const aiResponse = await getOpenAIChatCompletion([{role: "user", content: userInput}]);
    streamTo(data => res.write(`data: ${data}\n\n`), aiResponse);
    console.log("AI response streamed to client.");
    res.end();
  } catch (err) {
    console.error("Error occurred in getAndStreamOpenAIChatCompletion: ", err);
    res.status(500).json({ error: 'An error occurred while streaming AI response.' });
  }
}

console.log("POST route for /chat defined.");

// Set the server to listen on a given port
const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
