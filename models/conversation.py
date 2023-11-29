from . import db

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    messages = db.relationship('ChatMessage', backref='conversation', lazy=True)

    def __repr__(self):
        return f'<Conversation {self.title}>'
