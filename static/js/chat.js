/* chat.css located in the static/css directory */
#chat-container {
  max-width: 600px;
  margin: 30px auto;
  border: 1px solid #ddd;
  padding: 20px;
  border-radius: 5px;
  background-color: #f9f9f9;
}

#messages-list {
  list-style-type: none;
  padding: 0;
}

#messages-list li {
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

#message-form {
  margin-top: 20px;
}

#message-input {
  width: 80%;
  padding: 10px;
  margin-right: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

$('#message-form').submit(function(e) {
  e.preventDefault();
  const userMessage = $('#message-input').val();
  const conversationId = $('#conversation-select').val();  // Assuming you have a selector for conversations

  $.ajax({
      type: 'POST',
      url: '/send_message',
      contentType: 'application/json;charset=UTF-8',
      data: JSON.stringify({ 'message': userMessage, 'conversation_id': conversationId }),
      success: function(response) {
          // Update the chat window with the new message and AI response
          $('#chat-window').append(`<div>User: ${response.user_message}</div>`);
          $('#chat-window').append(`<div>AI: ${response.ai_response}</div>`);
          $('#message-input').val('');  // Clear the input field
      },
      error: function(error) {
          console.log('Error sending message:', error);
      }
  });
});
