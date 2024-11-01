
import os
import uuid
import pickle
import json
import boto3
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel
from fastapi import HTTPException
from llama_index.core import SummaryIndex, StorageContext, load_index_from_storage
from llama_index.core.schema import TextNode
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec
from pinecone import Index
from llama_parse import LlamaParse

from app.models.report_models import ReportOutput

# create stored_pages.json file


class ReportService:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.LLAMA_PARSED_DIR = "./llama_parsed"
        os.makedirs(self.LLAMA_PARSED_DIR, exist_ok=True)
        self.embedding_dimension = 3072
        self.index_name = "multimodalindex"
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.embed_model = OpenAIEmbedding(model="text-embedding-3-large", api_key=os.getenv("OPENAI_API_KEY"))
        self.llm = OpenAI(model="gpt-4o", system_prompt="You are a report generation assistant...")
        self.pinecone_index = self.setup_pinecone_index()
        self.stored_pages = self.load_stored_pages()
        self.output_dir = Path("output_reports")
        self.output_dir.mkdir(exist_ok=True)
        self.STORED_PAGES_FILE = "stored_pages.json"

    def setup_pinecone_index(self) -> Index:
        indexes = self.pc.list_indexes()
        if any(index['name'] == self.index_name for index in indexes.get('indexes', [])):
            pinecone_index = self.pc.Index(self.index_name)
        else:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            pinecone_index = self.pc.Index(self.index_name)
        return pinecone_index

    def download_pdf_from_s3(self, pdf_name: str) -> str:
        temp_dir = "/tmp/"
        pdf_path = os.path.join(temp_dir, f"{os.path.basename(pdf_name)}")
        try:
            self.s3_client.download_file("cfapublications", pdf_name, pdf_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error downloading PDF from S3: {str(e)}")
        return pdf_path

    def parse_document(self, pdf_path: str) -> List[dict]:
        parsed_file = os.path.join(self.LLAMA_PARSED_DIR, os.path.basename(pdf_path) + ".json")
        if os.path.exists(parsed_file):
            with open(parsed_file, "rb") as f:
                parsed_data = pickle.load(f)
        else:
            parser = LlamaParse(
                result_type="markdown",
                use_vendor_multimodal_model=True,
                vendor_multimodal_model_name="openai-gpt-4o-mini",
                api_key=os.getenv("LLAMA_PARSE_API_KEY")
            )
            parsed_data = parser.get_json_result(pdf_path)
            os.makedirs("data_images", exist_ok=True)
            os.makedirs(self.LLAMA_PARSED_DIR, exist_ok=True)
            parser.get_images(parsed_data, download_path="data_images")
            with open(parsed_file, "wb") as f:
                pickle.dump(parsed_data, f)
        return parsed_data

    def store_in_pinecone(self, parsed_data: List[dict]):
        try:
            for page_data in parsed_data:
                pdf_name = "Test PDF"
                for page in page_data.get("pages", []):
                    page_num = page.get("page")
                    page_text = page.get("md", "")
                    metadata = {
                        "page_num": page_num,
                        "pdf_name": pdf_name,
                        "text": page_text
                    }
                    if (pdf_name, page_num) in self.stored_pages:
                        continue
                    embedding = self.embed_model._get_text_embedding(page_text)
                    self.pinecone_index.upsert([{
                        "id": str(uuid.uuid4()),
                        "values": embedding,
                        "metadata": metadata
                    }])
                    self.stored_pages.add((pdf_name, page_num))
                    self.save_stored_pages()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error storing data in Pinecone: {str(e)}")

    def load_stored_pages(self) -> set:
        if os.path.exists(self.STORED_PAGES_FILE):
            with open(self.STORED_PAGES_FILE, "r") as f:
                return set(tuple(page) for page in json.load(f))
        return set()

    def save_stored_pages(self):
        with open(self.STORED_PAGES_FILE, "w") as f:
            json.dump([list(page) for page in self.stored_pages], f)

    def generate_structured_report(self, parsed_data: List[dict]) -> str:
        storage_dir = "storage_nodes_summary"
        text_nodes = self.get_text_nodes(parsed_data[0]["pages"], image_dir="data_images")
        if not os.path.exists(storage_dir):
            index = SummaryIndex(text_nodes)
            index.set_index_id("summary_index")
            index.storage_context.persist(storage_dir)
        else:
            storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
            index = load_index_from_storage(storage_context, index_id="summary_index")
        system_prompt = (
            "You are a report generation assistant. Generate a brief, single-paragraph summary "
            "that highlights key financial insights and any relevant visuals, keeping it under 100 words."
        )
        llm = OpenAI(model="gpt-4o", system_prompt=system_prompt)
        sllm = llm.as_structured_llm(output_cls=ReportOutput)
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            llm=sllm,
            response_mode="compact"
        )
        response = query_engine.query("Generate a concise financial summary.")
        markdown_output = self.process_response_to_markdown(response)
        return markdown_output

    def get_text_nodes(self, parsed_pages, image_dir=None):
        text_nodes = []
        image_files = self._get_sorted_image_files(image_dir) if image_dir else []
        combined_text = "\n".join(page.get("md", "") for page in parsed_pages)
        metadata = {"page_num": 1, "parsed_text_markdown": combined_text}
        if image_files:
            metadata["image_path"] = str(image_files[0])
        node = TextNode(text=combined_text, metadata=metadata)
        text_nodes.append(node)
        return text_nodes

    def _get_sorted_image_files(self, image_dir):
        raw_files = [f for f in list(Path(image_dir).iterdir()) if f.is_file()]
        return sorted(raw_files, key=self.get_page_number)

    def get_page_number(self, file_name):
        import re
        match = re.search(r"-page-(\d+)\.jpg$", str(file_name))
        return int(match.group(1)) if match else 0

    def process_response_to_markdown(self, response_instance) -> str:
        markdown_output = f"## Report Summary\n\n{response_instance.response.text}\n\n---\n\n"
        markdown_output += "### Source Details\n\n"
        for idx, node in enumerate(response_instance.source_nodes, start=1):
            metadata = node.node.metadata
            markdown_output += f"#### Page {metadata.get('page_num', idx)}\n\n"
            main_text = metadata.get("parsed_text_markdown", "").strip()
            if main_text:
                markdown_output += f"{main_text}\n\n"
            image_path = metadata.get("image_path")
            if image_path:
                markdown_output += f"![Image for Page {metadata['page_num']}]({image_path})\n\n"
            markdown_output += "---\n\n"
        return markdown_output

    def convert_markdown_to_pdf(self, markdown_content: str) -> str:
        import markdown
        import pdfkit
        html_content = markdown.markdown(markdown_content)
        output_path = self.output_dir / "report_summary.pdf"
        pdfkit.from_string(html_content, str(output_path))
        return str(output_path)

    def generate_report(self, pdf_name: str) -> str:
        pdf_path = self.download_pdf_from_s3(pdf_name)
        parsed_data = self.parse_document(pdf_path)
        self.store_in_pinecone(parsed_data)
        markdown_output = self.generate_structured_report(parsed_data)
        report_pdf_path = self.convert_markdown_to_pdf(markdown_output)
        return report_pdf_path
