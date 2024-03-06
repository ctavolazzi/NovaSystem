import OpenAI from 'openai';
import { OpenAIStream, StreamingTextResponse } from 'ai';
import { OPENAI_API_KEY } from '$env/static/private';
 
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
 
  // Ask OpenAI for a streaming chat completion given the prompt
  const response = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    stream: true,
    messages,
  });
 
  // Convert the response into a friendly text-stream
  const stream = OpenAIStream(response);
  // Respond with the stream
  return new StreamingTextResponse(stream);
}