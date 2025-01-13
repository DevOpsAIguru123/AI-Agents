import os
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile
)
from azure.search.documents import SearchClient
from openai import AzureOpenAI
from uuid import uuid4

# Load environment variables from .env file
load_dotenv()

# Get environment variables
endpoint = os.environ.get("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.environ.get("AZURE_FORM_RECOGNIZER_KEY")

if not endpoint or not key:
    raise ValueError(
        "Please set AZURE_FORM_RECOGNIZER_ENDPOINT and AZURE_FORM_RECOGNIZER_KEY environment variables in .env file"
    )

document_analysis_client = DocumentAnalysisClient(endpoint, AzureKeyCredential(key))

# Move configuration variables before they're used
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_KEY")
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_KEY")
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING_DEPLOYMENT")
INDEX_NAME = "vector-search-demo"

# Validate environment variables
required_vars = {
    "AZURE_SEARCH_ENDPOINT": SEARCH_ENDPOINT,
    "AZURE_SEARCH_KEY": SEARCH_API_KEY,
    "AZURE_OPENAI_KEY": OPENAI_API_KEY,
    "AZURE_OPENAI_ENDPOINT": OPENAI_ENDPOINT,
    "EMBEDDING_DEPLOYMENT": EMBEDDING_DEPLOYMENT
}

for var_name, var_value in required_vars.items():
    if not var_value:
        raise ValueError(f"Missing required environment variable: {var_name}")

# Set up clients
search_index_client = SearchIndexClient(
    endpoint=SEARCH_ENDPOINT, 
    credential=AzureKeyCredential(SEARCH_API_KEY)
)
search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT, 
    index_name=INDEX_NAME, 
    credential=AzureKeyCredential(SEARCH_API_KEY)
)
openai_client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    api_version="2024-02-01",
    azure_endpoint=OPENAI_ENDPOINT
)

def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    """Split text into smaller chunks of roughly `chunk_size` characters."""
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if sum(len(w) for w in current_chunk) + len(word) < chunk_size:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
    # Add the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a local PDF using Azure Document Intelligence (Form Recognizer)."""
    # Verify file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
    with open(pdf_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-document",
            document=f,
        )

    result = poller.result()

    extracted_text = []
    for page in result.pages:
        for line in page.lines:
            extracted_text.append(line.content)
    return "\n".join(extracted_text)

def index_exists() -> bool:
    try:
        search_index_client.get_index(INDEX_NAME)
        return True
    except Exception:
        return False

# Move create_vector_search_index function before it's used
def create_vector_search_index():
    fields = [
        SearchField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="vector-profile"
        )
    ]
    
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="vector-config",
                kind="hnsw",
                parameters={
                    "m": 4,
                    "efConstruction": 400,
                    "efSearch": 500,
                    "metric": "cosine"
                }
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="vector-config",
            )
        ]
    )
    
    try:
        # Delete existing index if it exists
        if index_exists():
            search_index_client.delete_index(INDEX_NAME)
            print(f"Deleted existing index '{INDEX_NAME}'")
        
        # Create new index
        index = SearchIndex(
            name=INDEX_NAME,
            fields=fields,
            vector_search=vector_search
        )
        
        result = search_index_client.create_or_update_index(index)
        print(f"Index '{INDEX_NAME}' created successfully.")
        return result
        
    except Exception as e:
        print(f"Error creating index: {str(e)}")
        raise

def get_openai_embedding(text: str) -> list[float]:
    """Generate embeddings for the given text using Azure OpenAI."""
    response = openai_client.embeddings.create(
        input=text,
        model=EMBEDDING_DEPLOYMENT
    )
    return response.data[0].embedding

def upload_documents(documents: list[dict]):
    """Upload documents to the Azure Cognitive Search index."""
    # Generate embeddings for each document
    for doc in documents:
        doc['content_vector'] = get_openai_embedding(doc['content'])
        if 'id' not in doc:
            doc['id'] = str(uuid4())
    
    results = search_client.upload_documents(documents)
    for result in results:
        if result.succeeded:
            print(f"Uploaded document ID: {result.key}")
        else:
            print(f"Failed to upload document ID: {result.key}")

# Example usage for chunks
def process_chunks(chunks: list[str]):
    documents = []
    for chunk in chunks:
        doc = {
            'id': str(uuid4()),
            'content': chunk,
        }
        documents.append(doc)
    
    upload_documents(documents)

from azure.search.documents.models import VectorizedQuery

def search_documents(query: str, top_k: int = 3):
    query_vector = get_openai_embedding(query)
    
    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=top_k,
        fields="content_vector"
    )
    
    results = search_client.search(
        search_text="*",
        vector_queries=[vector_query],
        select=["content"]
    )
    
    return [{"content": doc["content"]} for doc in results]

def chat_with_documents(user_query: str) -> str:
    """Chat with the documents using RAG (Retrieval-Augmented Generation)."""
    # Search for relevant documents
    relevant_docs = search_documents(user_query)
    
    # Construct the system message with context
    context = "\n".join([doc["content"] for doc in relevant_docs])
    system_message = f"""You are a helpful assistant. Use the following context to answer questions.
    If you cannot find the answer in the context, say so.
    
    Context:
    {context}"""
    
    # Generate response using Azure OpenAI
    response = openai_client.chat.completions.create(
        model="gpt-4o",  # Replace with your deployment name
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_query}
        ],
        temperature=0.7,
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    # Use an absolute path or relative path to your actual PDF file
    pdf_path = os.path.join(os.path.dirname(__file__), "docs", "sample.pdf")
    try:
        # Extract text from PDF
        pdf_text = extract_text_from_pdf(pdf_path)
        print("Extracted PDF text:", pdf_text[:300])

        # Create chunks from the extracted text
        chunks = chunk_text(pdf_text)
        print(f"Created {len(chunks)} chunks")

        # Create the vector search index if it doesn't exist
        if not index_exists():
            create_vector_search_index()
            print("Created vector search index")

        # Process and upload chunks
        process_chunks(chunks)
        print("Successfully processed and uploaded chunks to Azure Search")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    # Add chat example
    try:
        query = "What are the main points discussed in the document?"
        response = chat_with_documents(query)
        print("\nQ:", query)
        print("A:", response)
    except Exception as e:
        print(f"Chat error: {str(e)}")






