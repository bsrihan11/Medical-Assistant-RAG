from langchain_community.vectorstores import FAISS
import os
from langchain_mistralai import MistralAIEmbeddings
from app.log import logger


def load_vector_store():
    """
    Loads a FAISS vector store from disk using Mistral embeddings.

    Returns:
        vector_store: A FAISS vector store loaded with the given embeddings.

    Raises:
        FileNotFoundError: If the embeddings directory or index files do not exist.
    """
    
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    EMBEDDINGS_DIR = os.path.join(ROOT_DIR, "vector DB", "embeddings")
    
    if not os.path.exists(EMBEDDINGS_DIR):
        error_msg = f"Embeddings directory '{EMBEDDINGS_DIR}' does not exist. Please create it first."
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    index_path = os.path.join(EMBEDDINGS_DIR, "index.faiss")
    config_path = os.path.join(EMBEDDINGS_DIR, "index.pkl")

    if os.path.exists(index_path) and os.path.exists(config_path):
        embedding_model = MistralAIEmbeddings(
            model='mistral-embed',
            api_key=os.environ.get('MISTRAL_API_KEY'),
            wait_time=2
        )
        
        vector_store = FAISS.load_local(
            EMBEDDINGS_DIR,
            embedding_model,
            allow_dangerous_deserialization=True
        )
        
        logger.info("✅ FAISS vector store loaded from disk.")
        return vector_store
    else:
        error_msg = f"FAISS index files not found in '{EMBEDDINGS_DIR}'. Please ensure the vector store is created first."
        
        logger.error(error_msg)
        
        raise FileNotFoundError(error_msg)
