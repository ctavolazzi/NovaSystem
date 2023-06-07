document.querySelector('.big-button').addEventListener('click', () => {
  fetch('/button_press', { method: 'POST' })
  .then(response => response.json())
  .then(data => console.log(data.message));
});


var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('message', function(msg) {
    // This will be called whenever a 'message' event is emitted.
    // You can update the chat window here.
    $('#chat_box').append('<p>' + msg.data + '</p>'); // changed '#chat' to '#chat_box'
});

$('form#chat_form').submit(function(event) { // changed '#chat' to '#chat_form'
    socket.emit('message', {data: $('#message').val()});
    return false;
});
