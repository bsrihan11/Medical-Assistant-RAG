from langchain_mistralai import ChatMistralAI
from langchain_core.rate_limiters import InMemoryRateLimiter
import time
from langchain_mistralai import MistralAIEmbeddings
from app.config import RagConfig
from app.vector_store import load_vector_store
import logging


logger = logging.getLogger(__name__)


class RagLLM(ChatMistralAI):
    """A custom LLM class for Mistral AI with rate limiting and retry logic."""

    def __init__(self, *args, **kwargs):
        """Initialize the RagLLM with custom rate limiting and retry logic."""
        from langchain_core.rate_limiters import InMemoryRateLimiter
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=0.25,
            max_bucket_size=1,
            check_every_n_seconds=0.3
        )

        super().__init__(
            model="mistral-large-latest",
            temperature=0,
            max_retries=5,
            rate_limiter=rate_limiter,
            max_tokens=1250
        )

    def invoke(self, prompt):
        """
        Invoke the LLM with retry logic for rate limits.
        
        Retries with exponential backoff if rate limits are hit.
        """
        for attempt in range(10):
            try:
                return super().invoke(prompt)
            except Exception as e:
                wait_time = (2 ** (attempt+1)) * 0.5
                
                time.sleep(wait_time)
                
        raise RuntimeError("❌ Failed to invoke LLM after multiple retries. Please check your LLM subscription for more details.")



def create_retriever(vs):
    """
    Creates a retriever from the given vector store using MMR.

    Args:
        vs: The vector store instance.

    Returns:
        A configured retriever object.
    """
    
    retriever = vs.as_retriever(
        search_type="mmr",  # Enables Maximal Marginal Relevance
        search_kwargs={"k": 5, "lambda_mult": 0.5}  # Balance relevance and diversity
    )

    return retriever



def initialize_rag_pipeline():
    """
    Initializes the RAG pipeline: LLM, Embeddings, Vector Store, and Retriever.

    Returns:
        A tuple containing the LLM, embeddings model, vector store, and retriever.
    """
    
    try:
        logger.info("Initializing RAG LLM...")
        llm_model = RagLLM()

        logger.info("Loading Mistral embeddings model...")
        embedding_model = MistralAIEmbeddings(
            model='mistral-embed',
            api_key=RagConfig.MISTRAL_API_KEY,
            wait_time=2
        )

        logger.info("Loading or building FAISS vector store...")
        vector_store = load_vector_store()

        logger.info("Creating retriever from vector store...")
        retriever = create_retriever(vector_store)

        logger.info("RAG pipeline initialized successfully.")

        return llm_model, embedding_model, vector_store, retriever

    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {e}", exc_info=True)
        raise RuntimeError(f"❌ Failed to initialize RAG pipeline: {e}")
