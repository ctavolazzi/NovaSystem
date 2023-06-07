function streamResponseTo(message, outputHandler) {
  for (let i = 0; i < message.length; i++) {
      setTimeout(() => {
          outputHandler(message[i]);
      }, 35 * i);
  }
}
