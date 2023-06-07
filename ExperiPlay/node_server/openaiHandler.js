const { Configuration, OpenAIApi } = require("openai");

// Set up OpenAI configuration
const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});

const openai = new OpenAIApi(configuration);

async function getOpenAIChatCompletion(messages) {
  console.log('getOpenAIChatCompletion messages:\n', messages);''
  // Call the OpenAI API to get a chat completion
  const completion = await openai.createChatCompletion({
    model: 'gpt-3.5-turbo',
    messages: messages,
  });
  return completion.data.choices[0].message.content;
}

async function streamTo(outputHandler, message, delay = 35) {
  for (let i = 0; i < message.length; i++) {
    setTimeout(() => {
      outputHandler(message[i]);
    }, delay * i);
  }
  setTimeout(() => {
    outputHandler('\n');
  }, delay * message.length);
}


module.exports = {
  getOpenAIChatCompletion,
  streamTo
};
