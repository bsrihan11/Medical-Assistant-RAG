import os
from langchain_community.vectorstores import FAISS
from langchain_mistralai import MistralAIEmbeddings
import time
from vector_ops.chunks import create_chunks
from vector_ops.loader import load_documents    
from dotenv import load_dotenv
load_dotenv()

def load_vector_store(embedding_model, batch_size=50):
    """Load or create a FAISS vector store from the provided documents."""
    

    EMBEDDINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),'embeddings')
    
    embedding_model = MistralAIEmbeddings(
            model='mistral-embed',
            api_key= os.environ.get('MISTRAL_API_KEY'),
            wait_time=2
        )

    
    if not os.path.exists(EMBEDDINGS_DIR):
        
        print(f"Creating embeddings directory at {EMBEDDINGS_DIR}")
        os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    
    
    vector_store = None
    
    try:
        print("⚙️ Building FAISS vector store in batches...")
        start = time.time()

        os.makedirs(EMBEDDINGS_DIR, exist_ok=True)  
            
        doc  = load_documents()
        split_docs = create_chunks(doc)
            
            
        first_batch = split_docs[:batch_size]
        vector_store = FAISS.from_documents(first_batch, embedding_model)
        total_batches = (len(split_docs) + batch_size - 1) // batch_size

        print(f"Batch 1/{total_batches} completed")

            
        for i in range(batch_size, len(split_docs), batch_size):
            batch = split_docs[i:i + batch_size]
            vector_store.add_documents(batch)
            batch_num = (i // batch_size) + 1
            print(f"Batch {batch_num}/{total_batches} completed")

        vector_store.save_local(EMBEDDINGS_DIR)
        end = time.time()

        print(f"✅ FAISS DB created and saved at '{EMBEDDINGS_DIR}'")
        print(f"⏱️ Time taken: {int((end - start) // 60)} min {int((end - start) % 60)} sec")

        return vector_store
       
    except Exception as e:
        print(f"❌ Error creating FAISS vector store: {e}")
            
        return None



