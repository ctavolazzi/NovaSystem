import OpenAI from 'openai';
import { OpenAIStream, StreamingTextResponse } from 'ai';
import { OPENAI_API_KEY } from '$env/static/private';

import winston from 'winston';

const logger = winston.createLogger({
  transports: [
    new winston.transports.File({ filename: 'logs.txt' }),
  ],
});

logger.info('This is a log message!');

// Create an OpenAI API client (that's edge friendly!)
const openai = new OpenAI({
  apiKey: OPENAI_API_KEY,
});
 
// Set the runtime to edge for best performance
export const config = {
  runtime: 'edge'
};
 
export async function POST({ request }) {
  const { messages } = await request.json();
  console.log('messages', messages);
  logger.info(`messages: , ${JSON.stringify(messages)}`);

  // Save the messages to a file
  // const file = await Deno.open('messages.txt', { write: true, create: true, truncate: true });
  // await file.write(new TextEncoder().encode(JSON.stringify(messages)));
  // file.close();
  // This doesn't work, but it's a start
 
  // Ask OpenAI for a streaming chat completion given the prompt
  const response = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    stream: true,
    messages,
  });
 
  // console.log('response', response);
  // for await (const chunk of response) {
  //   console.log('chunk', chunk);
  // }
  // Convert the response into a friendly text-stream
  const stream = OpenAIStream(response);
  // Respond with the stream

  return new StreamingTextResponse(stream);

}