from langchain.text_splitter import RecursiveCharacterTextSplitter
import os



def create_chunks(doc):
    """Split documents into smaller chunks for efficient processing."""
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
        )   
    split_docs = splitter.split_documents(doc)  
    print(f'Total Chunks: {len(split_docs)}')   
    return split_docs

