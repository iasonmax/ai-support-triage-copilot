from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

def create_embedding_model():
    """Initialize Ollama embedding model."""
    return OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="http://localhost:11434"  # Adjust if Ollama runs on different port
    )

def load_knowledge_base(kb_dir: str = "app/knowledge_base"):
    """Load all markdown files from knowledge_base directory."""
    kb_path = Path(kb_dir)
    docs = []
    
    for md_file in kb_path.glob("*.md"):
        loader = TextLoader(str(md_file), encoding="utf-8")
        docs.extend(loader.load())
    
    return docs

def split_documents(docs, chunk_size: int = 500, chunk_overlap: int = 100):
    """
    Split documents into manageable chunks.
    - chunk_size: max characters per chunk
    - chunk_overlap: characters of overlap (helps context continuity)
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_documents(docs)

def get_or_create_chroma_store(chunks, embeddings, persist_dir: str = "app/chroma_db"):
    """Load existing store or create a new one."""
    if Path(persist_dir).exists():
        print("Loading existing vector store...")
        return load_chroma_store(embeddings, persist_dir)
    
    print("Creating new vector store...")
    return create_chroma_store(chunks, embeddings, persist_dir)

def create_chroma_store(chunks, embeddings, persist_dir: str = "app/chroma_db"):
    """
    Create ChromaDB vector store from chunks.
    persist_dir: where to save the database (survives restarts)
    """
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    return vector_store

def load_chroma_store(embeddings, persist_dir: str = "app/chroma_db"):
    """Load existing ChromaDB (if it exists)."""
    return Chroma(
        embedding_function=embeddings,
        persist_directory=persist_dir
    )

def retrieve_relevant_context(query: str, vector_store, k: int = 3):
    """Search for top k most relevant chunks."""
    results = vector_store.similarity_search_with_score(query, k=k)
    return results

def format_context(search_results):
    """Convert search results into readable context."""
    if not search_results:
        return "No relevant documentation found."
    
    context = "### Relevant Support Articles:\n\n"
    for i, (doc, score) in enumerate(search_results, 1):
        context += f"**Article {i}** (relevance: {score:.2f}):\n"
        context += doc.page_content + "\n\n"
    
    return context


if __name__ == "__main__":
    docs = load_knowledge_base()
    chunks = split_documents(docs)
    embeddings = create_embedding_model()
    vector_store = get_or_create_chroma_store(chunks, embeddings)

    test_queries = [
        "Adobe won't open",
        "printer is offline",
        "I forgot my password"
    ]

    for query in test_queries:
        print(f"\n--- Query: '{query}' ---")
        results = retrieve_relevant_context(query, vector_store, k=2)
        for doc, score in results:
            print(f"Score: {score:.3f}")
            print(f"Text: {doc.page_content[:150]}...\n")