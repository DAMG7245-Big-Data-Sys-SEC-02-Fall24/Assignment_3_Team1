import os

from fastapi import APIRouter, Depends, Form, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from fastapi import FastAPI, HTTPException, Request, status

from typing import List, Dict

from app.routes.helpers import ChatResponse, ChatRequest, load_chat_history, setup_chat_histories, DUMMY_IMAGE_URL, \
    save_chat_history, ChatHistoryResponse
from app.services import d_rag_service
from app.services.database_service import get_db
from app.services.auth_service import verify_token  # Assuming token validation is handled in auth_service
import logging
from fastapi.staticfiles import StaticFiles

from app.services.rag_service import summarize_document, query_chat

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


@router.get("/chat/history", response_model=ChatHistoryResponse, status_code=status.HTTP_200_OK)
async def get_chat_history_endpoint(document_id: str, token: str = Depends(oauth2_scheme)):
    """
    Retrieve the entire chat history for a given document ID.
    """
    user_email = verify_token(token)
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not document_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'document_id' query parameter is required."
        )

    chat_history = load_chat_history(document_id)
    if not chat_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No chat history found for document_id: {document_id}"
        )

    return ChatHistoryResponse(document_id=document_id, messages=chat_history)
