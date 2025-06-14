import logging
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOG_FILE = os.path.join(ROOT_DIR, 'backend', 'app.log')


logging.basicConfig(
    filename = LOG_FILE,              
    level=logging.INFO,              
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

logger = logging.getLogger(__name__)


from vector_ops.embed import create_vector_store
from langchain_mistralai import MistralAIEmbeddings

def init():
    """
    Initializes the vector store with embeddings.
    
    This function creates a vector store using MistralAI embeddings and stores it in the specified directory.
    """
    
    try:
        embedding_model = MistralAIEmbeddings(model='mistral-embed',api_key= os.environ['MISTRAL_API_KEY'],wait_time=2)
   
        create_vector_store(embedding_model = embedding_model)
        
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
        raise



