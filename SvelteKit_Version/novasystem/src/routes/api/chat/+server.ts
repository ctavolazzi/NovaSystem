// src/routes/api/chat/+server.ts
import { json } from '@sveltejs/kit';
// const { Request } = require('node-fetch');
import OpenAI from 'openai';


// load the .env file
import dotenv from 'dotenv';
dotenv.config();

// load the openai api key from the .env file
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const openai = new OpenAI(OPENAI_API_KEY);

export async function POST({ request }) {
  const { messages } = await request.json();

  try {
    const openaiResponse = await openai.Completion.create({
      model: "gpt-3.5-turbo",
      prompt: messages.map((m) => m.content).join("\n"),
      max_tokens: 150,
    });

    if (openaiResponse.data.choices[0].text) {
      return json({ response: openaiResponse.data.choices[0].text });
    } else {
      return json({ response: "No response from AI." });
    }
  } catch (error) {
    return json({ error: error.message }, { status: 500 });
  }
}
