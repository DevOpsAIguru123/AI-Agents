import streamlit as st
from langchain_core.messages import AIMessage
import os
from ..chat.rag_chat import RAGChat
from ..config.settings import *

class StreamlitUI:
    def __init__(self):
        self.setup_page()
        self.initialize_rag()
        
    def setup_page(self):
        """Setup the Streamlit page"""
        st.title(APP_TITLE)
        st.markdown(APP_DESCRIPTION)
        
    def initialize_rag(self):
        """Initialize the RAG system"""
        if "rag" not in st.session_state:
            st.session_state.rag = RAGChat(CHROMA_PERSIST_DIR)
            if not os.path.exists(DATA_PATH):
                st.error(f"Knowledge base file not found at {DATA_PATH}")
                return
                
            try:
                st.session_state.rag.ingest_documents(DATA_PATH)
            except Exception as e:
                st.error(f"Error loading knowledge base: {str(e)}")
                return
                
    def create_layout(self):
        """Create the main layout"""
        chat_col, history_col = st.columns([2, 1])
        return chat_col, history_col
        
    def display_chat_interface(self, chat_col):
        """Display the chat interface"""
        chat_col.markdown("### Chat")
        
        # Clear history button
        _, clear_col = chat_col.columns([4, 1])
        with clear_col:
            if st.button("Clear History"):
                st.session_state.rag.memory_manager.clear()
                st.rerun()
        
        # Display messages
        for message in st.session_state.rag.memory_manager.message_history:
            role = "assistant" if isinstance(message, AIMessage) else "user"
            with chat_col.chat_message(role):
                st.markdown(message.content)
                
    def display_history_sidebar(self, history_col):
        """Display the history sidebar"""
        history_col.markdown("### Conversation History")
        history = st.session_state.rag.memory_manager.message_history
        
        for i in range(0, len(history), 2):
            if i + 1 < len(history):
                with history_col.expander(f"Q: {history[i].content[:30]}..."):
                    st.markdown("**Question:**")
                    st.markdown(history[i].content)
                    st.markdown("**Answer:**")
                    st.markdown(history[i+1].content)
                    
    def handle_user_input(self, chat_col):
        """Handle user input"""
        if prompt := chat_col.chat_input("Ask your question"):
            try:
                response = st.session_state.rag.query(prompt)
                st.rerun()
            except Exception as e:
                chat_col.error(f"Error: {str(e)}")
                
    def run(self):
        """Run the Streamlit application"""
        chat_col, history_col = self.create_layout()
        self.display_chat_interface(chat_col)
        self.display_history_sidebar(history_col)
        self.handle_user_input(chat_col) 