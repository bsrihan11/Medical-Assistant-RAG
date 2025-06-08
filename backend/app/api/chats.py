from flask import Blueprint
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db
from app.rag import generate_summary, get_rag_reply, get_title
from app.models import User, Chat, ShortTermMemory, LongTermMemory


chats_bp = Blueprint('chats', __name__)



@chats_bp.route('/new', methods=['POST'])
@jwt_required()
def create_chat():
    """
    Create a new chat session for the authenticated user.

    Expects:
        JSON body with a 'query' field representing the user's initial message.

    Process:
        - Generates a title for the chat using the query.
        - Creates a new Chat record.
        - Generates a response using the RAG system.
        - Stores the initial query and response in ShortTermMemory.

    Returns:
        JSON response with the created chat data and HTTP 201 status,
        or an error if the query is missing.
    """
    
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



@chats_bp.route('/<int:chat_id>', methods=['GET', 'POST'])
@jwt_required()
def llm_chat(chat_id):
    """
    Retrieve or update a chat session.

    Methods:
        GET:
            - Returns chat metadata for the given chat_id.

        POST:
            - Accepts a new user query.
            - Uses last 2 messages and long-term memory to generate a response.
            - Stores query-response pair in short-term memory.
            - Updates long-term memory if message count exceeds 2.

    Expects:
        JSON body with a 'query' field (for POST).

    Returns:
        JSON response with chat or message data.
    """
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify(error='Chat not found'), 404

    if request.method == 'GET':
        return jsonify(chat.to_json()), 200

    
    data = request.get_json()
    query = data.get('query')

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    # Short-term memory: last 2 messages
    all_messages = ShortTermMemory.query.filter_by(chat_id=chat_id).all()
    recent_messages = all_messages[-2:]

    # Long-term memory (if exists)
    long_term_summary = LongTermMemory.query.filter_by(chat_id=chat_id).first()
    summary_text = long_term_summary.summary if long_term_summary else ""

    # Get RAG-based response
    answer = get_rag_reply(query, recent_messages, summary_text)

    # Store in short-term memory
    message = ShortTermMemory(chat_id=chat_id, question=query, answer=answer)
    db.session.add(message)
    db.session.commit()

    # Update long-term memory if more than 2 messages
    if len(all_messages) + 1 > 2:
        updated_summary = generate_summary(recent_messages + [message])
        if long_term_summary:
            long_term_summary.summary = updated_summary
        else:
            db.session.add(LongTermMemory(chat_id=chat_id, summary=updated_summary))
        db.session.commit()

    return jsonify(message.to_json()), 200



