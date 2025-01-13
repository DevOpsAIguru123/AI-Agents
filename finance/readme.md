# Finance AI Agent

A powerful document analysis and chat application that leverages Azure's AI services to process financial documents and enable interactive conversations about their content.

## Features

- 📄 PDF document processing and text extraction
- 🔍 Vector-based semantic search capabilities
- 💬 Interactive chat interface with document context
- 🧠 AI-powered responses using Azure OpenAI
- ⚡ Real-time document processing and indexing

## Prerequisites

- Azure subscription with access to:
  - Azure OpenAI Service
  - Azure Cognitive Search
  - Azure Document Intelligence (formerly Form Recognizer)
- Python 3.8 or higher

## Installation

1. Clone the repository:
bash
git clone [repository-url]
cd finance

2. Create a virtual environment:
bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

3. Install dependencies:
bash
pip install -r requirements.txt

4. Set up environment variables:
bash
cp .env.example .env

5. Configure Azure services:

- Azure OpenAI Service:
  - Create a new Azure OpenAI resource
  - Note your endpoint and API key
  - Create a new deployment named "gpt-4o"

- Azure AI Search:
  - Create a new Azure AI Search resource
  - Note your endpoint and API key
  - Create a new index named "vector-search-demo"

- Azure Document Intelligence (Form Recognizer):
  - Create a new Azure Document Intelligence resource
  - Note your endpoint and API key

6. Run the application:
bash
streamlit run finance.py

## Usage

1. Upload a PDF document
2. The application will process the document and create embeddings
3. You can now ask questions about the document

## License

This project is licensed under the MIT License. See the LICENSE file for details.


