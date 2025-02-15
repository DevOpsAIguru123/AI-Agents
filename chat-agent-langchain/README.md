# ISRO Info Assistant

A Retrieval-Augmented Generation (RAG) based chat system that answers questions about ISRO (Indian Space Research Organisation) using LangChain, OpenAI, and ChromaDB.

## Features

- 🤖 Conversational AI powered by GPT-4
- 📚 Document retrieval using ChromaDB vector store
- 💾 Persistent chat history
- 🎯 Context-aware responses
- 🖥️ User-friendly Streamlit interface

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd isro-info-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Start the application:
```bash
streamlit run main.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Start asking questions about ISRO!

## Features in Detail

### RAG System
- Uses OpenAI embeddings for document vectorization
- ChromaDB for efficient similarity search
- Contextual question answering with chat history

### Memory Management
- Persistent chat history
- Conversation context maintenance
- File-based history storage

### User Interface
- Clean, intuitive Streamlit interface
- Chat history sidebar
- Clear history functionality

## Configuration

Key settings can be modified in `src/config/settings.py`:

- `MODEL_NAME`: OpenAI model to use
- `CHUNK_SIZE`: Document chunk size for processing
- `RETRIEVER_K`: Number of similar documents to retrieve
- File paths and other constants

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LangChain for the RAG framework
- OpenAI for language models
- ChromaDB for vector storage
- Streamlit for the UI framework
