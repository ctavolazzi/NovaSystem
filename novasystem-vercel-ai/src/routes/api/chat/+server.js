// /Users/ctavolazzi/Code/NovaSystem/novasystem-vercel-ai/src/routes/api/chat/+server.js

import OpenAI from 'openai';
import { OpenAIStream, StreamingTextResponse } from 'ai';
import { OPENAI_API_KEY, MONGODB_URI } from '$env/static/private';

console.log('OPENAI_API', OPENAI_API_KEY);
console.log('MONGODB_URI', MONGODB_URI);

import winston from 'winston';
import mongoose from 'mongoose';

// Set up Winston logger
const logger = winston.createLogger({
  transports: [
    new winston.transports.File({ filename: 'logs.txt' }),
  ],
});

// Connect to MongoDB database
mongoose.connect(MONGODB_URI, {
  serverSelectionTimeoutMS: 30000, // Increase the timeout value if needed
})
  .then(() => {
    console.log('Connected to MongoDB');
  })
  .catch((error) => {
    console.error('Connection error', error);
  });

// Define Chat schema
const chatSchema = new mongoose.Schema({
  title: String,
  messages: [{ role: String, content: String }],
});

// Create Chat model
const Chat = mongoose.model('Chat', chatSchema);

// Create an OpenAI API client (that's edge friendly!)
const openai = new OpenAI({
  apiKey: OPENAI_API_KEY,
});

// Set the runtime to edge for best performance
export const config = {
  runtime: 'edge'
};

export async function POST({ request }) {
  console.log('Received POST request to /api/chat');
  const { chatId, messages } = await request.json();
  console.log(`chatId: ${chatId}`);
  console.log(`messages: ${JSON.stringify(messages)}`);

  try {
    const chat = await Chat.findByIdAndUpdate(
      chatId,
      { $push: { messages: { $each: messages } } },
      { new: true }
    );
  
    if (!chat) {
      console.log('Chat not found');
      return new Response('Chat not found', { status: 404 });
    }
  
    // Rest of the code...
    } catch (error) {
      console.error('Error querying the database:', error);
      return new Response('Internal Server Error', { status: 500 });
  }
    // Ask OpenAI for a streaming chat completion given the prompt
    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      stream: true,
      messages: chat.messages,
    });

    // Convert the response into a friendly text-stream
    const stream = OpenAIStream(response);

    // Respond with the stream
    return new StreamingTextResponse(stream);
  } catch (error) {
    logger.error('Error in POST request:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
}

export async function GET({ params }) {
  const { chatId } = params;

  try {
    // Find the chat by ID and return its messages
    const chat = await Chat.findById(chatId);

    if (!chat) {
      return new Response('Chat not found', { status: 404 });
    }

    return new Response(JSON.stringify(chat.messages), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    logger.error('Error in GET request:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
}

export async function PUT({ request, params }) {
  const { chatId } = params;
  const { title } = await request.json();

  try {
    // Find the chat by ID and update its title
    const chat = await Chat.findByIdAndUpdate(chatId, { title }, { new: true });

    if (!chat) {
      return new Response('Chat not found', { status: 404 });
    }

    return new Response(JSON.stringify(chat), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    logger.error('Error in PUT request:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
}

export async function DELETE({ params }) {
  const { chatId } = params;

  try {
    // Find the chat by ID and delete it
    const chat = await Chat.findByIdAndDelete(chatId);

    if (!chat) {
      return new Response('Chat not found', { status: 404 });
    }

    return new Response('Chat deleted', { status: 200 });
  } catch (error) {
    logger.error('Error in DELETE request:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
}