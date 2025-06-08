from langchain_community.document_loaders import PyPDFLoader
from vector_ops import logger
import os

def load_documents():
    '''Load and preprocess documents from a PDF file for RAG'''
    
    DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__),'documents')
    
    PDF_FILENAME = 'The-Gale-Encyclopedia-of-Medicine-3rd-Edition-staibabussalamsula.ac_.id_.pdf'
    
    if not os.path.exists(os.path.join(DOCUMENTS_DIR, PDF_FILENAME)): 
        path_msg = f"PDF file '{PDF_FILENAME}' not found in {DOCUMENTS_DIR}"
        logger.error(path_msg)
        raise FileNotFoundError(path_msg)
    
    
    pdf_path = os.path.join(DOCUMENTS_DIR, PDF_FILENAME)
    pdf_loader = PyPDFLoader(pdf_path)
    
    doc  = pdf_loader.load()
    doc = doc[30:4091]
    return doc

