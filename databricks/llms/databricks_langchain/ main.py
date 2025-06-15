import os
from dotenv import load_dotenv
from databricks_langchain import ChatDatabricks

# Load credentials from .env file or environment variables
load_dotenv()

# Check for required credentials
host = os.getenv("DATABRICKS_HOST")
token = os.getenv("DATABRICKS_TOKEN")
if not host or not token:
    raise EnvironmentError(
        "Please set DATABRICKS_HOST and DATABRICKS_TOKEN as environment variables or in a .env file."
    )

# Set up the Foundation Model (replace with your actual endpoint/model name)
chat_model = ChatDatabricks(
    model="databricks-meta-llama-3-3-70b-instruct",  # Change to your foundation model if needed
    host=host,
    api_key=token,
    temperature=0.1,
    max_tokens=256
)

print("Welcome to your Databricks LLM chat! Type 'exit' or 'quit' to leave.")

while True:
    user_input = input("You: ")
    if user_input.strip().lower() in {"exit", "quit"}:
        print("Goodbye!")
        break

    try:
        response = chat_model.invoke(user_input)
        print("Assistant:", response.content)
    except Exception as e:
        print(f"Error: {e}")
