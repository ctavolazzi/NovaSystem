document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  const userInput = document.querySelector('input[name="userInput"]');
  const chatOutput = document.getElementById('chat-output');

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    // Create a new paragraph for the user's message and add it to the chat output
    const userPara = document.createElement('p');
    userPara.textContent = `You: ${userInput.value}`;
    chatOutput.appendChild(userPara);

    // Send a request to the server with the user's message
    fetch('/chat', { method: 'POST', body: JSON.stringify({ userInput: userInput.value }), headers: { 'Content-Type': 'application/json' } })
      .then(response => {
        // Get the readable stream
        const reader = response.body.getReader();
        const stream = new ReadableStream({
          start(controller) {
            function push() {
              reader.read().then(({ done, value }) => {
                if (done) {
                  controller.close();
                  return;
                }
                controller.enqueue(value);
                push();
              })
            }
            push();
          }
        });
        return new Response(stream, { headers: { 'Content-Type': 'text/plain' } }).text();
      })
      .then(data => {
        // Display the AI's response
        const aiPara = document.createElement('p');
        aiPara.textContent = `AI: ${data}`;
        chatOutput.appendChild(aiPara);
      })
      .catch(error => {
        console.error('Error:', error);
      });

});
