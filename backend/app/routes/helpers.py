import json
import logging
import os
from typing import List

from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)

def setup_chat_histories():
    if not os.path.exists(CHAT_HISTORY_DIR):
        os.makedirs(CHAT_HISTORY_DIR)
CHAT_HISTORY_DIR = "chat_histories"
DUMMY_IMAGE_URL = "http://localhost:8000/static/images/sample.jpg"




class ChatRequest(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the chat session.")
    message: str = Field(..., description="The user's message to the assistant.")

    class Config:
        schema_extra = {
            "example": {
                "document_id": "doc123",
                "message": "Hello, how are you?"
            }
        }


class ChatResponse(BaseModel):
    role: str = Field(..., description="Role of the message sender (e.g., 'assistant').")
    content: str = Field(..., description="Markdown-formatted response from the assistant.")

    class Config:
        schema_extra = {
            "example": {
                "role": "assistant",
                "content": "# Assistant Response\n\n**You said:** Hello, how are you?\n\n![Dummy Image](https://via.placeholder.com/150)\n\n*This is a dummy response in Markdown.*"
            }
        }


class ChatHistoryResponse(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the chat session.")
    messages: List[ChatResponse] = Field(..., description="List of all chat messages exchanged.")

    class Config:
        schema_extra = {
            "example": {
                "document_id": "doc123",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, how are you?"
                    },
                    {
                        "role": "assistant",
                        "content": "# Assistant Response\n\n**You said:** Hello, how are you?\n\n![Dummy Image](https://via.placeholder.com/150)\n\n*This is a dummy response in Markdown.*"
                    }
                ]
            }
        }


# Utility Functions

def get_chat_history_file(document_id: str) -> str:
    """
    Returns the file path for a given document ID's chat history.
    """
    cwd = os.getcwd()
    directory = cwd + "/chat_histories/assignment3/pdfs/"
    js = cwd + f"/chat_histories/{document_id}_chat.json"
    history_path = os.path.join(directory, f"{document_id}_chat.json")
    #    if nested directory is not present, create it
    if not os.path.exists(directory):
        logging.info(f"Creating directory: {directory}")
        os.makedirs(directory)
    # if json file does not exist, create it
    if not os.path.exists(js):
        logging.info(f"Creating chat history file: {js}")
        with open(js, "w") as f:
            json.dump({}, f)


    return js


def load_chat_history(document_id: str) -> List[dict]:
    """
    Loads the chat history for a given document ID.
    """
    filepath = get_chat_history_file(document_id)
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data.get("messages", [])
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in {filepath}.")
            return []


def save_chat_history(document_id: str, messages: List[dict]):
    """
    Saves the chat history for a given document ID.
    """
    filepath = get_chat_history_file(document_id)
    data = {
        "document_id": document_id,
        "messages": messages
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
