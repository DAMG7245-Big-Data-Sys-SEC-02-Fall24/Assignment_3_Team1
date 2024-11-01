import json
import os
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from fastapi import FastAPI, HTTPException, Request, status

from typing import List, Dict

from app import services
from app.routes.helpers import ChatResponse, ChatRequest, load_chat_history, setup_chat_histories, \
    save_chat_history, ChatHistoryResponse, markdown_to_pdf

from app.services.database_service import get_db
from app.services.auth_service import verify_token  # Assuming token validation is handled in auth_service
import logging
from fastapi.staticfiles import StaticFiles

from app.services.rag_service import summarize_document, query_chat
from app.services.tools import tools

# Initialize the router for document routes
router = APIRouter()

# Define OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Configure logging
logging.basicConfig(level=logging.INFO)
class SummaryRequest(BaseModel):
    document_name: str

@router.post("/summarize", tags=["Summary"])
async def summarize_endpoint(
        summary_request: SummaryRequest,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    Endpoint to summarize a document.
    """
    try:
        # Verify the JWT token
        user_email = verify_token(token)
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Extract summary parameters from the request body
        document_name = summary_request.document_name
        response = summarize_document(document_name)
        logging.info(f"Summary response: {response}")
        logging.info("----------------------")
        return {"markdown": response}

    except Exception as e:
        logging.error(f"An error occurred during the summary process: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while summarizing the document: {str(e)}")

@router.post("/report", tags=["Summary"])
async def summarize_endpoint(
        publication_id: int,
        summary_request: Dict[str, str] = Body(...),
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    Endpoint to summarize a document.
    """
    try:
        # Verify the JWT token
        user_email = verify_token(token)
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Extract summary parameters from the request body
        document_name = summary_request.get("document_name")
        response = summarize_document(document_name)
        return {"markdown": response}

    except Exception as e:
        logging.error(f"An error occurred during the summary process: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while summarizing the document: {str(e)}")

setup_chat_histories()


# API Endpoints

@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(chat_request: ChatRequest, token: str = Depends(oauth2_scheme)):
    """
    Handle chat queries. Returns a Markdown response and persists the conversation.
    """
    user_email = verify_token(token)
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    document_id = chat_request.document_id
    user_message = chat_request.message.strip()

    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'message' field must not be empty."
        )

    # Load existing chat history
    chat_history = load_chat_history(document_id)

    # Append the user's message
    user_entry = {
        "role": "user",
        "content": user_message
    }

    chat_history.append(user_entry)

    # Generate a dummy Markdown response
    assistant_response =query_chat(chat_request.document_id, chat_request.message)

    assistant_entry = {
        "role": "assistant",
        "content": assistant_response
    }
    chat_history.append(assistant_entry)

    # Persist the updated chat history
    save_chat_history(document_id, chat_history)

    return ChatResponse(**assistant_entry)

notes_dir = os.getcwd() + "/notes/assignment3/pdfs/"
chat_histories_dir = os.getcwd() + "/chat_histories/assignment3/pdfs/"
directory_path = Path(notes_dir)
chat_path = Path(chat_histories_dir)
from fastapi.responses import FileResponse

@router.get("/list-files")
async def list_files():
    """
    List all files in the specified directory.
    """
    if not chat_path.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found")

    # Get all file names in the directory

    files = [file.stem.replace("_chat", "") for file in chat_path.iterdir() if file.is_file()]

    return {"files": files}
def read_json(file_path: str) -> str:
    """Reads a JSON file and returns its content."""
    try:
        with open(file_path, 'r') as file:
            return json.dumps(json.load(file))
    except Exception as e:
        return f"Error reading JSON file: {str(e)}"

@router.post("/download-file")
async def download_file(request:dict):
    """
    Download a specified PDF file.
    """
    # json_file =
    logging.info(f"Downloading file: {request["filename"]}")
    json_file = chat_histories_dir + request["filename"] + "_chat.json"
    print(json_file)
    json_extract = read_json(json_file)
    query = "-----Below is a chat history of the document. I want you to create a well formatted markdown of this. Dont repeat any questions if occuring twice-----\n" + json_extract
    assistant_response = query_chat("assignment3/pdfs/" + request['filename'], query)
    print(assistant_response)
    markdown_to_pdf(assistant_response, notes_dir +  request['filename'])
    file_path = Path(notes_dir + request["filename"] + ".pdf")
    # Check if file exists and is a PDF
    if not file_path.exists() or not file_path.is_file() or file_path.suffix.lower() != '.pdf':
        raise HTTPException(status_code=404, detail="File not found or not a PDF")

    return FileResponse(path=file_path, filename=request["filename"], media_type='application/pdf')