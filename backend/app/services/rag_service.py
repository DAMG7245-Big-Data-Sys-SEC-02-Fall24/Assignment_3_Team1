from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os
import boto3
import uuid
import pickle
from llama_index.core import DocumentSummaryIndex, StorageContext, load_index_from_storage
from llama_parse import LlamaParse
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from pinecone import Index
embedding_dimension = 3072
from typing import List
import pinecone
from pinecone import Pinecone, ServerlessSpec
import os
import dotenv
from llama_index.core.evaluation import RelevancyEvaluator
from typing import List
from llama_index.core.schema import TextNode
from pydantic import BaseModel
from typing import List
import uuid
from fastapi import HTTPException

import os
import json
import uuid
from typing import List, Tuple
from fastapi import HTTPException

index_name = "multimodalindex"
s3_client = boto3.client('s3')
LLAMA_PARSED_DIR = "llama_parsed"
os.makedirs(LLAMA_PARSED_DIR, exist_ok=True)


dotenv.load_dotenv()
print(os.getenv("PINECONE_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

import os
from pathlib import Path
from typing import List
from llama_index.core.schema import TextNode
from llama_index.core import SummaryIndex, StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel, Field


# Define a simplified response format
class ReportOutput(BaseModel):
    text: str = Field(..., description="A concise summary of the document with key insights.")


# Helper function to get sorted image files
def get_page_number(file_name):
    import re
    match = re.search(r"-page-(\d+)\.jpg$", str(file_name))
    return int(match.group(1)) if match else 0


def _get_sorted_image_files(image_dir):
    raw_files = [f for f in list(Path(image_dir).iterdir()) if f.is_file()]
    return sorted(raw_files, key=get_page_number)


# Function to process text and images, and create text nodes
def get_text_nodes(parsed_pages, image_dir=None):
    text_nodes = []
    image_files = _get_sorted_image_files(image_dir) if image_dir else []
    print("Image files:", image_files)
    # Combine all pages into one node for simplicity
    combined_text = "\n".join(page.get("md", "") for page in parsed_pages)
    metadata = {"page_num": 1, "parsed_text_markdown": combined_text}

    # Attach the first relevant image if present
    if image_files:
        metadata["image_path"] = str(image_files[0])

    node = TextNode(text=combined_text, metadata=metadata)
    text_nodes.append(node)
    return text_nodes


# Function to summarize and generate a concise report
import asyncio


async def generate_structured_report_async(parsed_data: List[dict]):
    # Prepare data for summary index
    storage_dir = "storage_nodes_summary"
    text_nodes = get_text_nodes(parsed_data[0]["pages"], image_dir="data_images")

    # Create or load summary index
    if not os.path.exists(storage_dir):
        index = SummaryIndex(text_nodes)
        index.set_index_id("summary_index")
        index.storage_context.persist(storage_dir)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        index = load_index_from_storage(storage_context, index_id="summary_index")

    # System prompt to generate a concise report
    system_prompt = (
        "You are a report generation assistant. Generate a brief, single-paragraph summary "
        "that highlights key financial insights and any relevant visuals, keeping it under 100 words."
    )
    llm = OpenAI(model="gpt-4o", system_prompt=system_prompt)
    sllm = llm.as_structured_llm(output_cls=ReportOutput)

    # Query the summary index for a concise report (await to ensure blocking behavior)
    query_engine = index.as_query_engine(
        similarity_top_k=5,
        llm=sllm,
        response_mode="compact"
    )

    response = await query_engine.query("Generate a concise financial summary.")

    print(response)
    return response


# Synchronous wrapper to run the async function in a blocking manner
def generate_structured_report(parsed_data: List[dict]):
    return asyncio.run(generate_structured_report_async(parsed_data))


def setup_pinecone_index(pc, index_name: str, embedding_dimension: int) -> pinecone.Index:
    """
    Checks if the specified index_name exists in Pinecone.
    If it exists, connects to the index; if not, creates the index with specified parameters.

    Args:
        pc: The Pinecone client object.
        index_name (str): The name of the index to check or create.
        embedding_dimension (int): The embedding dimension for the index.

    Returns:
        pinecone.Index: The Pinecone index object.
    """
    # Retrieve the list of indexes
    indexes = pc.list_indexes()

    # Check if the index_name exists in the list
    if any(index['name'] == index_name for index in indexes.get('indexes', [])):
        print(f"[INFO] Index '{index_name}' exists. Connecting to it.")
        pinecone_index = pc.Index(index_name)
    else:
        print(f"[INFO] Index '{index_name}' does not exist. Creating it.")
        pinecone_index = pc.create_index(
            name=index_name,
            dimension=embedding_dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        pinecone_index = pc.Index(index_name)
        print(f"[INFO] Index '{index_name}' created successfully.")

    return pinecone_index


embed_model = OpenAIEmbedding(model="text-embedding-3-large", api_key=os.getenv("OPENAI_API_KEY"))
llm = OpenAI(model="gpt-4o", system_prompt="You are a report generation assistant...")
pinecone_index = setup_pinecone_index(pc, index_name, embedding_dimension)
print(pinecone_index)

class PDFRequest(BaseModel):
    pdf_name: str = Field(..., description="The name of the PDF file in S3 to be processed.")

def download_pdf_from_s3(pdf_name: str) -> str:
    temp_dir = "/tmp/"
    # Set a clear, fixed path with UUID for uniqueness
    pdf_path = os.path.join(temp_dir, f"{os.path.basename(pdf_name)}")
    try:
        # Ensure the file downloads to the specified path without suffix
        s3_client.download_file("cfapublications", pdf_name, pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading PDF from S3: {str(e)}")
    return pdf_path

def parse_document(pdf_path: str) -> str:
    """Use LlamaParse to parse a document if it hasn’t been parsed before."""
    parsed_file = os.path.join(LLAMA_PARSED_DIR, os.path.basename(pdf_path) + ".json")
    if os.path.exists(parsed_file):
        print("[INFO] Using cached parsed file.")
        with open(parsed_file, "rb") as f:
            parsed_data = pickle.load(f)
    else:
        print("[INFO] Parsing document using LlamaParse.")
        parser = LlamaParse(
            result_type="markdown",
            use_vendor_multimodal_model=True,
            vendor_multimodal_model_name="openai-gpt-4o-mini",
            api_key=os.getenv("LLAMA_PARSE_API_KEY")
        )
        parsed_data = parser.get_json_result(pdf_path)
        os.makedirs("data_images", exist_ok=True)
        os.makedirs(LLAMA_PARSED_DIR, exist_ok=True)
        image_dicts = parser.get_images(parsed_data, download_path="data_images")
        with open(parsed_file, "wb") as f:
            pickle.dump(parsed_data, f)
    return parsed_data


STORED_PAGES_FILE = "stored_pages.json"


# Load the stored pages from the file at startup
def load_stored_pages() -> set:
    """Load stored pages from a JSON file."""
    if os.path.exists(STORED_PAGES_FILE):
        with open(STORED_PAGES_FILE, "r") as f:
            return set(tuple(page) for page in json.load(f))
    return set()


# Save the stored pages to the file
def save_stored_pages(stored_pages: set):
    """Save stored pages to a JSON file."""
    with open(STORED_PAGES_FILE, "w") as f:
        json.dump([list(page) for page in stored_pages], f)


# Initialize stored pages set from the file
stored_pages = load_stored_pages()


def store_in_pinecone(parsed_data: List[dict]):
    """
    Stores parsed PDF data in Pinecone, checking if each page has already been stored based on pdf_name and page_num.

    Args:
        parsed_data (List[dict]): List of dictionaries containing page data.

    Raises:
        HTTPException: If an error occurs while storing data in Pinecone.
    """
    print("[INFO] Storing parsed data in Pinecone.")

    try:
        for page_data in parsed_data:
            pdf_name = "Test PDF"  # Assuming a single PDF name; replace if dynamic

            for page in page_data.get("pages", []):
                page_num = page.get("page")
                page_text = page.get("md", "")
                metadata = {
                    "page_num": page_num,
                    "pdf_name": pdf_name,
                    "text": page_text
                }

                # Check if this page is already tracked locally
                if (pdf_name, page_num) in stored_pages:
                    print(f"[INFO] Page {page_num} of '{pdf_name}' already exists in Pinecone. Skipping storage.")
                    continue

                # Embed and store the new page if not found in local cache
                embedding = embed_model._get_text_embedding(page_text)
                print(f"[INFO] Storing page {page_num} of '{pdf_name}' in Pinecone.")

                pinecone_index.upsert([{
                    "id": str(uuid.uuid4()),
                    "values": embedding,
                    "metadata": metadata
                }])

                # Add the page to the local cache and save to file
                stored_pages.add((pdf_name, page_num))
                save_stored_pages(stored_pages)  # Persist the updated set
                print(f"[INFO] Successfully stored page {page_num} of '{pdf_name}' in Pinecone.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing data in Pinecone: {str(e)}")


# Function to evaluate responses
def evaluate_response(query: str, response: str):
    evaluator = RelevancyEvaluator()
    eval_result = evaluator.evaluate_response(query=query, response=response)
    if eval_result.passing:
        print("[INFO] Response is relevant.")
    else:
        print("[WARNING] Response may not be relevant.")
    return eval_result.passing


def get_pinecone_data(query: str):
    """Retrieve relevant data from Pinecone based on query."""
    query_embedding = embed_model.embed_text(query)
    result = pinecone_index.query(query_embedding, top_k=5, include_metadata=True)
    context = " ".join([item['metadata']['text'] for item in result['matches']])
    return context

def generate_summary(parsed_data: dict):
    """Generate a summary of the parsed document using the LLM."""
    print("[INFO] Generating summary for the document.")
    storage_context = StorageContext.from_defaults(persist_dir=LLAMA_PARSED_DIR)
    summary_index = DocumentSummaryIndex.build_index_from_nodes(parsed_data, service_context=storage_context)
    return summary_index.query("Provide a comprehensive summary of the document content.")


def get_page_number(file_name):
    import re
    match = re.search(r"-page-(\d+)\.jpg$", str(file_name))
    return int(match.group(1)) if match else 0


def _get_sorted_image_files(image_dir):
    """Get image files sorted by page."""
    raw_files = [f for f in list(Path(image_dir).iterdir()) if f.is_file()]
    sorted_files = sorted(raw_files, key=get_page_number)
    return sorted_files


# Function to process text and images, and create text nodes
def get_text_nodes(parsed_pages, image_dir=None):
    text_nodes = []
    image_files = _get_sorted_image_files(image_dir) if image_dir else []

    for idx, page in enumerate(parsed_pages):
        md_text = page.get("md", "")
        metadata = {"page_num": idx + 1, "parsed_text_markdown": md_text}
        if idx < len(image_files):
            metadata["image_path"] = str(image_files[idx])
        node = TextNode(text="", metadata=metadata)
        text_nodes.append(node)

    return text_nodes

from typing import List, Dict
from fastapi import HTTPException

def retrieve_relevant_entries(pdf_name: str, top_k: int = 5) -> List[Dict]:
    """
    Retrieve top-k entries from Pinecone filtered by pdf_name.

    Args:
        pdf_name (str): The name of the PDF to filter by.
        top_k (int): The number of top entries to retrieve.

    Returns:
        List[Dict]: A list of dictionaries containing the text, page number, and image path of each entry.
    """
    try:
        # Define the metadata filter
        metadata_filter = {"pdf_name": {"$eq": pdf_name}}

        # Perform the query with the metadata filter
        query_response = pinecone_index.query(
            vector=[0] * embedding_dimension,  # Dummy vector for metadata-only filtering
            top_k=top_k,
            include_metadata=True,
            include_values=False,
            filter=metadata_filter
        )

        # Extract relevant information from the query response
        relevant_nodes = [
            {
                "text": match["metadata"].get("text"),
                "page_num": match["metadata"].get("page_num"),
                "image_path": match["metadata"].get("image_path")
            }
            for match in query_response["matches"]
        ]

        print(f"[INFO] Retrieved {len(relevant_nodes)} relevant entries for {pdf_name}.")
        return relevant_nodes

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data from Pinecone: {str(e)}")
# Function to summarize and generate structured responses
def generate_structured_report(parsed_data: List[dict], top_k: int = 5):
    """
    Generate a structured summary report for a given PDF using only the top-k relevant entries.
    """
    pdf_name = parsed_data[0].get("pdf_name", "Document")

    # Step 1: Retrieve relevant entries from Pinecone for the specified PDF
    relevant_entries = retrieve_relevant_entries(pdf_name, top_k=top_k)

    # Step 2: Process relevant entries into TextNodes
    text_nodes = []
    for entry in relevant_entries:
        node = TextNode(
            text=entry["text"],
            metadata={
                "page_num": entry["page_num"],
                "image_path": entry["image_path"],
                "parsed_text_markdown": entry["text"]
            }
        )
        text_nodes.append(node)

    # Step 3: Create or load summary index for filtered data
    storage_dir = "storage_nodes_summary"
    if not os.path.exists(storage_dir):
        index = SummaryIndex(text_nodes)
        index.set_index_id("summary_index")
        index.storage_context.persist(storage_dir)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        index = load_index_from_storage(storage_context, index_id="summary_index")

    # Step 4: Set up query engine for structured output
    system_prompt = (
        "You are a report generation assistant tasked with generating a structured summary. "
        "Use images only when necessary to supplement detailed sections. "
        "Output your response as a series of text and image blocks. Keep it less than 100 words."
    )
    llm = OpenAI(model="gpt-4o", system_prompt=system_prompt)
    sllm = llm.as_structured_llm(output_cls=ReportOutput)

    query_engine = index.as_query_engine(
        similarity_top_k=top_k,
        llm=sllm,
        response_mode="compact"
    )

    # Step 5: Generate the structured report
    response = query_engine.query("Summarize key financial insights and visuals.")
    return response


def generate_report(pdf_request: PDFRequest):
    try:
        pdf_path = download_pdf_from_s3(pdf_request.pdf_name)
        parsed_data = parse_document(pdf_path)

        store_in_pinecone(parsed_data)
        summary = generate_summary(parsed_data)
        return {"status": "Report generated", "summary": summary.response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def chat_with_pdf(query: str, pdf_name: str):
    try:
        context = get_pinecone_data(query)
        response = llm.query(f"Context: {context}\n\nQuestion: {query}")
        return {"status": "Chat successful", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


import nest_asyncio

nest_asyncio.apply()


def generate_report_endpoint(pdf_name: str):
    pdf_path = download_pdf_from_s3(pdf_name)
    print(pdf_path)

    # Parse the PDF
    parsed_data = parse_document(pdf_path)
    print("[INFO] Parsed data:", parsed_data)

    # Store in Pinecone
    store_in_pinecone(parsed_data)
    print("[INFO] Data stored in Pinecone.")

    # Generate a structured report
    report_response = generate_structured_report(parsed_data)
    print("[INFO] Report generated successfully.")
    return report_response




# Define a class structure for the response if needed, else pass the response directly to this function

def process_response_to_markdown(response_instance) -> str:
    """
    Converts the Pydantic response instance containing text and image data into a plain Markdown format.

    Args:
        response_instance (BaseModel): The response instance containing the summary and source nodes.

    Returns:
        str: The formatted Markdown output.
    """
    # Check if the response_instance has the expected attributes
    print("-------Response to markdown----------")
    print(response_instance)
    if not hasattr(response_instance, "response") or not hasattr(response_instance, "source_nodes"):
        raise ValueError("The response instance does not have the expected 'response' and 'source_nodes' attributes.")

    # Access the text summary from the response
    markdown_output = f"## Report Summary\n\n{response_instance.response.text}\n\n---\n\n"
    markdown_output += "### Source Details\n\n"

    # Iterate through source nodes
    for idx, node in enumerate(response_instance.source_nodes, start=1):
        metadata = node.node.metadata
        markdown_output += f"#### Page {metadata.get('page_num', idx)}\n\n"

        # Extract main text if available
        main_text = metadata.get("parsed_text_markdown", "").strip()
        if main_text:
            markdown_output += f"{main_text}\n\n"

        # Include image if available
        image_path = metadata.get("image_path")
        if image_path:
            markdown_output += f"![Image for Page {metadata['page_num']}]({image_path})\n\n"

        # Horizontal rule for separation
        markdown_output += "---\n\n"

    return markdown_output


# Example usage:
# Assuming `response_instance` is an actual instance of the response object returned by your LLM query
# markdown = process_response_to_markdown(response_instance)
# print(markdown)

if __name__ == "__main__":
    report_response = generate_report_endpoint(pdf_name="assignment3/pdfs/The Economics of Private Equity_ A Critical Review.pdf")
    print(report_response)
    # markdown_op = process_response_to_markdown(report_response)
    # print(markdown_op)
    # output_dir = Path("output_reports")
    # output_dir.mkdir(exist_ok=True)  # Create the directory if it doesn't exist
    # output_path = output_dir / "report_summary.md"
    #
    # with open(output_path, "w") as f:
    #     f.write(markdown_op)
    # print(f"[INFO] Markdown content has been saved to {output_path}")

