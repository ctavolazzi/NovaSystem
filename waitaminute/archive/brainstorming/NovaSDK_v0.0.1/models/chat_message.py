# models/chat_message.py

from app import db

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.String, nullable=False)
    ai_response = db.Column(db.String, nullable=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)

    def __repr__(self):
        return f'<ChatMessage {self.user_message}>'
