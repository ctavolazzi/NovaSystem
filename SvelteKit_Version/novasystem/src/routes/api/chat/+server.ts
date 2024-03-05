// src/routes/api/chat/+server.ts
import { json } from '@sveltejs/kit';
import { OpenAI } from 'openai'; // This line might need to change

// Load the .env file
import dotenv from 'dotenv';
dotenv.config();

// Load the openai api key from the .env file
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
console.log("Loading API KEY...")
console.log(OPENAI_API_KEY);

// Check how Configuration should be used based on the openai package documentation
// This could be a function or an object, not necessarily a class to be instantiated
// For example, if it's a singleton object or function:
const client = new OpenAI(OPENAI_API_KEY);

export async function POST({ request }) {
  try {
    const body = await request.json();
    const completion = await client.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: body.messages,
    });

    if (completion.data.choices && completion.data.choices.length > 0) {
      return json({ message: completion.data.choices[0].message.content });
    } else {
      return json({ message: 'No response from AI.' });
    }
  } catch (error) {
    console.error('OpenAI error:', error);
    return json({ error: error.message }, { status: 500 });
  }
}
