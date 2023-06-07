const { Configuration, OpenAIApi } = require("openai");

// Configuration for OpenAI
const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

// Function to get the OpenAI chat completion
async function getOpenAIChatCompletion(userInput) {
    const completion = await openai.createChatCompletion({
      model: "gpt-3.5-turbo",
      messages: [{role: "user", content: userInput}],
    });
    return completion.data.choices[0].message.content;
}

// Function to stream the response to a specified outputHandler
function streamResponseTo(message, outputHandler) {
    for (let i = 0; i < message.length; i++) {
        setTimeout(() => {
            outputHandler(message[i]);
        }, 35 * i);
    }
    setTimeout(() => {
        outputHandler('\n');
    }, 35 * message.length);
}


module.exports = {
    getOpenAIChatCompletion,
    streamResponseTo
};
