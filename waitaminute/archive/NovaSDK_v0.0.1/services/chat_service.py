from app import db
from models.chat_message import ChatMessage
from models.conversation import Conversation

def process_user_message(user_message):
    # Here you will call the AI API, get the response, and save both the user message
    # and the AI response to the database. For now, let's use a placeholder AI response.
    ai_response = call_ai_api(user_message)

    # Let's assume all messages belong to a single conversation for simplicity.
    # In a real application, you would determine the appropriate conversation.
    conversation = Conversation.query.first()
    if not conversation:
        conversation = Conversation(title="General")
        db.session.add(conversation)
        db.session.commit()

    new_message = ChatMessage(user_message=user_message, ai_response=ai_response, conversation=conversation)
    db.session.add(new_message)
    db.session.commit()

    return {'user_message': user_message, 'ai_response': ai_response}

def get_last_messages():
    # Retrieve the last 10 messages from the database for display.
    return ChatMessage.query.order_by(ChatMessage.id.desc()).limit(10).all()

def call_ai_api(user_message):
    # Placeholder for AI API call
    # You would replace this with an actual call to the OpenAI API
    # and process the response accordingly.
    ai_response = "This is a placeholder response from the AI."
    return ai_response
