import type { RequestHandler } from './$types';
import OpenAI, { OpenAIStream, StreamingTextResponse } from 'openai';
import fs from 'fs';
import path from 'path';

// Create an OpenAI API client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || '',
});

// Create a simple in-memory cache
const cache = new Map();

export const POST: RequestHandler = async ({ request }) => {
  // Extract the `prompt` from the body of the request
  const { messages } = await request.json();

  // Generate a cache key based on the messages
  const key = JSON.stringify(messages);

  // Check if we have a cached response
  const cachedResponse = cache.get(key);
  if (cachedResponse) {
    return new StreamingTextResponse(cachedResponse);
  }

  // Ask OpenAI for a streaming chat completion given the prompt
  const response = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    stream: true,
    messages: messages.map((message: any) => ({
      content: message.content,
      role: message.role,
    })),
  });

  // Convert the response into a friendly text-stream
  const stream = OpenAIStream(response);

  // ...

  // Cache the response
  cache.set(key, stream);

  // Define the path to the log file
  const logFolderPath = path.join(__dirname, 'ChatLog');
  const logFilePath = path.join(logFolderPath, 'messages.log');

  try {
    // Ensure the log folder exists
    fs.mkdirSync(logFolderPath, { recursive: true });

    // Create a write stream to the log file, with the 'a' flag to append to the file
    const logStream = fs.createWriteStream(logFilePath, { flags: 'a' });

    // Write the current date, time, and messages to the log file
    logStream.write(`\n${new Date().toISOString()} - ${JSON.stringify(messages)}`);

    // Close the write stream, effectively saving the data to the file
    logStream.end();
  } catch (error) {
    console.error(`Failed to write to log file at ${logFilePath}:`, error);
  }

  // Respond with the stream
  return new StreamingTextResponse(stream);
};