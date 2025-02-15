from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
import json
from datetime import datetime

class MemoryManager:
    def __init__(self):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.message_history = []
        
    def save_interaction(self, question: str, answer: str):
        """Save an interaction to both memory systems"""
        self.memory.save_context(
            {"input": question},
            {"output": answer}
        )
        
        self.message_history.append(HumanMessage(content=question))
        self.message_history.append(AIMessage(content=answer))
        
    def clear(self):
        """Clear all memory"""
        self.memory.clear()
        self.message_history = []
        
    def save_to_file(self, filename="chat_history.json"):
        """Save chat history to file"""
        history = {
            "timestamp": datetime.now().isoformat(),
            "messages": [
                {
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content
                }
                for msg in self.message_history
            ]
        }
        
        with open(filename, "w") as f:
            json.dump(history, f, indent=2)
            
    def load_from_file(self, filename="chat_history.json"):
        """Load chat history from file"""
        try:
            with open(filename, "r") as f:
                history = json.load(f)
                messages = history.get("messages", [])
                
                self.message_history = []
                for msg in messages:
                    if msg["role"] == "user":
                        self.message_history.append(HumanMessage(content=msg["content"]))
                    else:
                        self.message_history.append(AIMessage(content=msg["content"]))
                        
                return self.message_history
        except FileNotFoundError:
            return [] 