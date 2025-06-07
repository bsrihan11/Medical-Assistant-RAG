from app import db


class User(db.Model):
    """Represents a user in the system."""
    
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)

    chats = db.relationship('Chat', backref='messanger', cascade="all, delete-orphan")

    def __init__(self, email, name):
        
        self.name = name
        self.email = email

    def to_json(self):
        
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'chats': [chat.to_json(basic=True) for chat in self.chats]
        }



class Chat(db.Model):
    """Represents a chat session between a user and the system."""
    
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(256))

    messages = db.relationship('ShortTermMemory', backref='parent_chat', cascade="all, delete-orphan")
    long_term_memories = db.relationship('LongTermMemory', backref='parent_chat', cascade="all, delete-orphan")

    def __init__(self, user_id, title):
        
        self.user_id = user_id
        self.title = title

    def to_json(self, basic=False):
        
        data = {
            'chat_id': self.id,
            'user_id': self.user_id,
            'title': self.title,
        }
        if not basic:
            data['messages'] = [m.to_json() for m in self.messages]
            data['long_term_memory'] = [ltm.to_json() for ltm in self.long_term_memories]
        return data



class ShortTermMemory(db.Model):
    """Represents a single message turn in a chat, including both user query and AI output."""
    
    __tablename__ = 'short_term_memory'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)

    def __init__(self, chat_id, question, answer):
        
        self.chat_id = chat_id
        self.question = question
        self.answer = answer

    def to_json(self):
        
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer
        }



class LongTermMemory(db.Model):
    """Stores long-term memory (summarized info) associated with a chat."""
    
    __tablename__ = 'long_term_memory'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    summary = db.Column(db.Text)

    def __init__(self, chat_id, summary):
        
        self.chat_id = chat_id
        self.summary = summary

    def to_json(self):
        
        return {
            'id': self.id,
            'summary': self.summary
        }
