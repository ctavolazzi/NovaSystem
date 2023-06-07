$(document).ready(function() {
  // Connect to the Socket.IO server.
  // The connection URL has the following format:
  //     http[s]://<domain>:<port>[/<namespace>]
  var socket = io.connect('http://' + document.domain + ':' + location.port);

  // Event handler for new messages.
  // The callback function is invoked whenever a 'message' event is emitted
  // by the server.
  socket.on('message', function(msg) {
      // Append the message to the chat.
      $('#chat').append('<p>' + msg.data + '</p>');
  });

  // Event handler for the chat form.
  $('form#chat').submit(function(event) {
      event.preventDefault();

      // Get the message text from the form.
      var messageText = $('#message').val();

      // Emit a 'message' event with the message text.
      socket.emit('message', {data: messageText});

      // Clear the message text in the form.
      $('#message').val('');
  });
});
