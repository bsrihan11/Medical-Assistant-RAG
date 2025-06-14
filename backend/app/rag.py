from langchain.prompts import PromptTemplate
from app.llm import initialize_rag_pipeline
from app.models import ShortTermMemory, LongTermMemory
from app import db
llm_model, embedding_model, vector_store, retriever = initialize_rag_pipeline()


def format_messages(messages):
    """
    Formats conversation messages into a structured text format.

    Args:
        messages: A list of message objects containing 'question' and 'answer'.

    Returns:
        A string representation of the conversation.
    """
    
    if len(messages) == 0:
        return ""
    formatted_messages = []
    for message in messages:
        formatted_messages.append('User: ' + message.question)
        formatted_messages.append('AI: ' + message.answer)

    return "\n".join(formatted_messages)


def generate_summary(chat):
    """
    Generates a summary of the conversation using the LLM.

    Args:
       chat: A Chat object containing previous messages.

    Returns:
        The generated summary string.
    """

    ltm_exists = LongTermMemory.query.filter_by(chat_id=chat.id).first()
    ltm = None

    if ltm_exists:
        ltm = ltm_exists.summary

    if ltm:
        # - First check for relevance of the last new chat message to existing summary
        last_message = format_messages(chat.messages[:-1])
        relevance_prompt = PromptTemplate(
            input_variables=["summary", "new_message"],
            template="""
            Determine if the following new message is relevant enough to update the given summary.

            [Current Summary]
            {summary}

            [New Message]
            {new_message}

            Instructions:
            - If the message contains new or important information related to the summary, any new goal or topic discusion say "Yes".
            - If the message is irrelevant or too trivial or already covered in Current Summary, say "No".

            Reply with only "Yes" or "No".
            """
        )

        relevance_check = llm_model.invoke(relevance_prompt.format(
            summary=ltm,
            new_message=last_message
        )).content.strip().lower()

        # - If relevant, append it to the summary, by summarising again using that summary and the last message
        if relevance_check == "yes":

            update_prompt = PromptTemplate(
                input_variables=["summary", "new_message"],
                template="""
                You are an AI assistant tasked with updating a summary with new relevant conversation content.

                [Existing Summary]
                {summary}

                [New Message]
                {new_message}

                Instructions:
                - Concisely incorporate the new information into the existing summary.
                - Maintain clarity and avoid redundancy.
                - Keep the total summary within approximately 1500 tokens.

                Updated Summary:
                """
            )
            updated_summary = llm_model.invoke(update_prompt.format(
                summary=ltm,
                new_message=last_message
            )).content.strip()

            ltm_exists.summary = updated_summary
            db.session.commit()

            return updated_summary

        else:
            # If not relevant, return the existing summary
            return ltm

    else:
        # Create a new summary if no long-term memory exists
        full_chat = format_messages(chat.messages)

        new_summary_prompt = PromptTemplate(
            input_variables=["messages_tb_summarized"],
            template="""
            You are an AI assistant tasked with summarizing a conversation between a human and an AI assistant.
            Please write a clear and concise summary of the following conversation.

            Conversation:
            {messages_tb_summarized}
            
            Instructions:
            - Focus on key questions, responses, decisions, and outcomes. 
            - Keep the tone professional and informative. 
            - Avoid including filler phrases or unrelated small talk.
            - Limit the summary to approximately 1250 tokens or fewer.
            """
        )

        new_summary = llm_model.invoke(new_summary_prompt.format(
            messages_tb_summarized=full_chat
        )).content.strip()

        # Store in DB
        new_ltm = LongTermMemory(chat_id=chat.id, summary=new_summary)
        db.session.add(new_ltm)
        db.session.commit()

        return ltm


def optimize_query(query, chat):
    """
    Rewrites a user follow-up query into a standalone question using recent chat history.

    This function retrieves the last 3 messages from the short-term memory of a chat session,
    formats them into a structured chat history, and combines them with the user’s follow-up input.
    It then prompts a language model to generate a complete, context-rich standalone version of the query.

    Args:
        query (str): The follow-up query entered by the user that requires contextual rewriting.
        chat (Chat): A Chat object containing metadata like chat ID used to retrieve recent messages.

    Returns:
        str: A rewritten, contextually complete standalone question derived from the follow-up query.
    """
    
    
    messages = ShortTermMemory.query.filter_by(chat_id=chat.id).all()[-3:]
    
    chat_history = format_messages(messages)
    
    prompt_template = PromptTemplate(
        input_variables=["chat_history", "user_query"],
        template="""
        You are an expert at rewriting questions. Given the following chat conversation and a follow-up user query, rewrite the query into a complete, standalone question that includes all relevant context from the conversation.

        Rules:
        - Preserve all clinical or contextually important details.
        - Do NOT include any instructions, explanations, or extra text.
        - Output ONLY the rewritten standalone question. No preamble, labels, or other formatting.

        Chat History:
        {chat_history}

        Follow-Up Input:
        {user_query}

        Standalone question:
        """
    )
    
    prompt = prompt_template.format(
        chat_history=chat_history,
        user_query=query
    )

    new_query = llm_model.invoke(prompt)
    
    return new_query.content.strip()



def get_title(first_query):
    """
    Generates a concise 5-token title summarizing the user's first query.

    Args:
        first_query: The initial user query string.

    Returns:
        A 5-token title string generated by the LLM.
    """
    
    title_prompt = PromptTemplate(
        input_variables=["query"],
        template="""
        You are an AI assistant that creates concise and descriptive titles for user queries.

        Task: Generate a 5-token title (no more, no less) that clearly summarizes the user's query.
        Avoid punctuation unless absolutely necessary, and use relevant keywords.

        Query:
        {query}

        5-token Title:
        """
    )

    prompt = title_prompt.format(query=first_query)
    response = llm_model.invoke(prompt)

    return response.content.strip()


def get_rag_reply_v2(query, chat):
    """
    Generates a RAG-based reply to a user query using memory and retrieved documents.

    Args:
        query: The user's current query.
        chat: The chat object containing previous messages and memories.

    Returns:
        A string response generated by the LLM.
    """

    # Fetch and format short-term memory
    
    optimized_query = query
    
    messages = []
    short_term = None
    if len(chat.messages) != 0:
        messages = ShortTermMemory.query.filter_by(
            chat_id=chat.id).all()[-3:]
        short_term = format_messages(messages)
        
        optimized_query = optimize_query(query, chat)

    # Fetch long-term memory summary
    long_term = None
    
    lts = LongTermMemory.query.filter_by(chat_id=chat.id).first()
    long_term = lts.summary if lts else None

    # Retrieve documents
    retrieved_docs = retriever.get_relevant_documents(query)
    retrieved_text = "\n".join(doc.page_content for doc in retrieved_docs) if len(
        retrieved_docs) > 0 else None

    # Build the dynamic prompt
    sections = [f"You are a trusted, careful AI medical assistant.",
                f"\n[User Query]\n{optimized_query}"]

    if retrieved_text:
        sections.append(f"\n[Relevant Medical Documents]\n{retrieved_text}")
    if long_term:
        sections.append(f"\n[Long-Term Memory]\n{long_term}")
    if short_term:
        sections.append(f"\n[Short-Term Memory]\n{short_term}")

    sections.append("""
        Instructions:
        - Use only the above mentioned information if available.
        - If unsure, refer the user to a doctor.
        - Do not mention or reference any documents, memory, context source, or prior chat turns in your answer.

        Response:""")

    prompt = "\n".join(sections)

    # Generate and return the AI response
    ai_response = llm_model.invoke(prompt)
    return ai_response.content
