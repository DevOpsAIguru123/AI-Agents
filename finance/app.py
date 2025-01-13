import streamlit as st
from finance import chat_with_documents, extract_text_from_pdf, chunk_text, process_chunks, create_vector_search_index, index_exists
import os

st.set_page_config(page_title="Document Chat", page_icon="📚")

st.title("💬 Chat with Your Documents")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# File uploader
uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")

if uploaded_file:
    # Save the uploaded file temporarily
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    try:
        # Extract and process the document
        with st.spinner("Processing document..."):
            # Extract text from PDF
            pdf_text = extract_text_from_pdf(temp_path)
            
            # Create chunks
            chunks = chunk_text(pdf_text)
            
            # Create index if it doesn't exist
            if not index_exists():
                create_vector_search_index()
            
            # Process and upload chunks
            process_chunks(chunks)
            
            st.success("Document processed successfully!")
    
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your documents"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    try:
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_with_documents(prompt)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")

# Add sidebar with instructions
with st.sidebar:
    st.markdown("""
    ## How to use
    1. Upload a PDF document using the file uploader
    2. Wait for the document to be processed
    3. Ask questions about the document in the chat
    
    ## About
    This app uses Azure OpenAI and Azure Cognitive Search to provide intelligent responses based on your documents.
    """)
