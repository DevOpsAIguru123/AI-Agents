from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import TextLoader
from .memory_manager import MemoryManager

class RAGChat:
    def __init__(self, persist_directory="chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0)
        self.vectorstore = None
        self.memory_manager = MemoryManager()
        
    def ingest_documents(self, file_path):
        """
        Ingest documents into the vector store
        """
        loader = TextLoader(file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        
    def setup_rag_chain(self):
        """
        Set up the RAG chain for question answering
        """
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        template = """Answer the question based on the following context and chat history:

        Context: {context}
        
        Chat History: {chat_history}
        
        Question: {question}
        
        Answer the question in a conversational manner while maintaining context from previous interactions.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        chain = (
            {
                "context": retriever, 
                "chat_history": lambda x: self.memory_manager.memory.load_memory_variables({})["chat_history"],
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
        )
        
        return chain
    
    def query(self, question: str) -> str:
        """
        Query the RAG system with a question
        """
        if not self.vectorstore:
            raise ValueError("No documents have been ingested. Please ingest documents first.")
        
        chain = self.setup_rag_chain()
        response = chain.invoke(question)
        
        self.memory_manager.save_interaction(question, response.content)
        return response.content 