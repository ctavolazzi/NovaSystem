$('#message-form').submit(function(e) {
  e.preventDefault();
  const userMessage = $('#message-input').val();
  if (!userMessage) return; // Don't send empty messages

  $.ajax({
      type: 'POST',
      url: '/send_message',
      contentType: 'application/json;charset=UTF-8',
      data: JSON.stringify({ 'message': userMessage }),
      success: function(response) {
          // Append the user's message and the AI response to the chat
          $('#messages-list').append(`<li><strong>You:</strong> ${userMessage}</li>`);
          $('#messages-list').append(`<li><strong>AI:</strong> ${response.ai_response}</li>`);
          $('#message-input').val(''); // Clear the input field
      },
      error: function(error) {
          console.error('Error sending message:', error);
      }
  });
});

// Assuming this JavaScript is within your chat.js file

$(document).ready(function() {
  $('#message-form').submit(function(e) {
      e.preventDefault();
      const userMessage = $('#message-input').val();
      if (!userMessage) return;  // Don't send empty messages

      $.ajax({
          type: 'POST',
          url: '/send_message',
          contentType: 'application/json;charset=UTF-8',
          data: JSON.stringify({ 'message': userMessage }),
          success: function(response) {
              // Append the user's message and the AI response to the chat
              $('#messages-list').append(`<li><strong>You:</strong> ${userMessage}</li>`);
              $('#messages-list').append(`<li><strong>AI:</strong> ${response.ai_response}</li>`);
              $('#message-input').val('');  // Clear the input field
              // Scroll to the bottom of the chat container
              $('#chat-container').scrollTop($('#chat-container')[0].scrollHeight);
          },
          error: function(error) {
              console.error('Error sending message:', error);
          }
      });
  });
});
