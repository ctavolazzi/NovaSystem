let responseMessage = '';

function streamToConsole(message) {
    for (let i = 0; i < message.length; i++) {
        setTimeout(() => {
            process.stdout.write(message[i]);
        }, 35 * i);
    }
}

async function getAIResponse(userInput) {
    // Your logic for calling the AI API.
    // For now, just return a placeholder response.
    return `AI's response: ${userInput}`;
}

function streamAIResponse(userInput) {
    getAIResponse(userInput)
        .then((response) => {
            responseMessage = response;
            streamToConsole(responseMessage);
        })
        .catch((err) => {
            console.error(`Error: ${err}`);
        });
}

streamAIResponse("Hello, world!");


function streamToHandler(message, outputHandler) {
  for (let i = 0; i < message.length; i++) {
      setTimeout(() => {
          outputHandler(message[i]);
      }, 35 * i);
  }
}

function consoleOutputHandler(character) {
  process.stdout.write(character);
}

// Define more output handlers as needed...

async function getAIResponse(userInput) {
  // Your logic for calling the AI API.
  // For now, just return a placeholder response.
  return `AI's response: ${userInput}`;
}

function streamAIResponse(userInput, outputHandler) {
  getAIResponse(userInput)
      .then((response) => {
          streamToHandler(response, outputHandler);
      })
      .catch((err) => {
          console.error(`Error: ${err}`);
      });
}

streamAIResponse("Hello, world!", consoleOutputHandler);



let responseMessage = '';

// The default handler prints to the console
function defaultOutputHandler(character) {
    process.stdout.write(character);
}

function streamToHandler(message, outputHandler = defaultOutputHandler) {
    for (let i = 0; i < message.length; i++) {
        setTimeout(() => {
            outputHandler(message[i]);
        }, 35 * i);
    }
}

async function getAIResponse(userInput) {
    // Your logic for calling the AI API.
    // For now, just return a placeholder response.
    return `AI's response: ${userInput}`;
}

// If no handler is provided, it defaults to the console
function streamAIResponse(userInput, outputHandler) {
    getAIResponse(userInput)
        .then((response) => {
            responseMessage = response;
            streamToHandler(responseMessage, outputHandler);
        })
        .catch((err) => {
            console.error(`Error: ${err}`);
        });
}

// Default case, streaming to console
streamAIResponse("Hello, world!");

// Custom case, streaming to a custom handler
function customOutputHandler(character) {
    // Custom logic here
    console.log(`Received character: ${character}`);
}
streamAIResponse("Hello, world!", customOutputHandler);
