from flask import Blueprint
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db
from app.rag import generate_summary, get_rag_reply, get_title
from app.models import User, Chat, ShortTermMemory, LongTermMemory


chats_bp = Blueprint('chats', __name__)

@chats_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_chat():

    user_id = get_jwt_identity()
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    
    return jsonify(user.to_json()), 200





@chats_bp.route('/new', methods=['POST'])
@jwt_required()
def create_chat():
    
    data = request.get_json()
    user_id = get_jwt_identity()
    
    query = data.get('query')


    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    title = get_title(query)
    
    c = Chat(user_id = user_id, title = title)
    db.session.add(c)
    db.session.commit()
    
    rag_output = get_rag_reply(query, [], "")
    
    
    message = ShortTermMemory(chat_id = c.id, question = query, answer = rag_output)
    db.session.add(message)
    db.session.commit()

    return jsonify(c.to_json()), 201




@chats_bp.route('/<int:chat_id>', methods=['GET','POST'])
@jwt_required()
def get_chat(chat_id):
    
    c = Chat.query.get(chat_id)
    if not c:
            return jsonify(error = 'Chat not found'), 404
    if request.method == 'GET':
            
        return jsonify(c.to_json()), 200
    
    else:
        
        data = request.get_json()
        query = data.get('query')
    
        if not query:
            return jsonify({'error': 'Query is required'}), 400


        # Step 1: Get Short-Term Memory (last 2 messages)
        all_msg = ShortTermMemory.query.filter_by(chat_id = chat_id).all()
        
        messages = all_msg[-2:] if len(all_msg) >= 2 else all_msg
        

        # Step 2: Get Long-Term Memory Summary (if exists)
        ltm = LongTermMemory.query.filter_by(chat_id = chat_id).first()
        long_term_summary = ltm.summary if ltm else ""


        # Step 3: Get Assistant Response
        response = get_rag_reply(query, messages, long_term_summary)


        # Step 4: Store Message
        msg = ShortTermMemory(chat_id = chat_id, question = query, answer = response)
        db.session.add(msg)
        db.session.commit()


        # Optional: Update Long-Term Memory if messages exceed 2
        if len(all_msg) + 1 > 2:
            
            summary = generate_summary(messages + [msg])  
            
            ltm = LongTermMemory.query.filter_by(chat_id = chat_id).first()
            
            if ltm:
                ltm.summary = summary
            else:
                ltm = LongTermMemory(chat_id=chat_id, summary=summary)
                db.session.add(ltm)
            
            db.session.commit()

        return jsonify(msg.to_json()), 200



