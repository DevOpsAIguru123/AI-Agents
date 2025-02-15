import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application settings
APP_TITLE = "ISRO Info Assistant"
APP_DESCRIPTION = "Ask questions about ISRO (Indian Space Research Organisation)"

# File paths
DATA_PATH = "data/data.txt"
CHAT_HISTORY_PATH = "chat_history.json"
CHROMA_PERSIST_DIR = "chroma_db"

# Model settings
MODEL_NAME = "gpt-4o"
MODEL_TEMPERATURE = 0

# Retriever settings
RETRIEVER_K = 3
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200 