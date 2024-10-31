from app.services.gpt import EvaluationModel, evaluate
from app.services.mongo import MongoDBFactory
from fastapi import HTTPException
from app.config.settings import settings
import logging

# MongoDB URI and database name
database_name = "pdf_database"

# Initialize the MongoDB factory
mongo_factory = MongoDBFactory(uri=settings.MONGO_URI, database_name=database_name)


class DocumentService:

    @staticmethod
    def query_and_evaluate_document(collection_name: str, pdf_name: str, query_text: str, gpt_model: str,
                                    objective: str):
        """
        Query a document and evaluate it with the specified GPT model and objective.
        """
        try:
            # Query the document from MongoDB
            document = mongo_factory.db_helper.find_document_by_pdf_name(collection_name, pdf_name)
            if not document:
                raise HTTPException(status_code=404,
                                    detail=f"No document found for pdf_name '{pdf_name}' in collection '{collection_name}'")

            # Extract text, tables, and images from the document pages
            document_text, file_attachments = DocumentService.extract_content_from_pages(document)
            logging.info(f"Extracted document content from {len(document.get('pages', []))} pages.")
            logging.info(f"Document text length: {len(document_text)} characters.")
            # Build the evaluation model for OpenAI
            evaluation_model = EvaluationModel(
                objective=objective,
                file_attachments=file_attachments,  # Attach images and tables
                model=gpt_model,
                query=query_text,
                additional_context=document_text  # Add the document text as context
            )

            # Call the evaluate function
            evaluated_response = evaluate(evaluation_model)
            return evaluated_response.response  # Return the response from the evaluation

        except Exception as e:
            logging.error(f"An error occurred while querying and evaluating the document: {str(e)}")
            raise HTTPException(status_code=500,
                                detail=f"An error occurred while querying and evaluating the document: {str(e)}")

    @staticmethod
    def extract_content_from_pages(document):
        """
        Extract text, tables, and images from the document's pages.
        Returns:
            - document_text (str): Combined text from all pages.
            - file_attachments (list): List of unique table and image URLs.
        """
        document_text = []
        file_attachments = set()  # Use a set to avoid duplicate entries

        try:
            pages = document.get('pages', [])

            # Iterate through the pages
            for page in pages:
                # Extract text
                page_text = page.get('text', '')
                document_text.append(page_text)

                # Extract tables and add them to file_attachments
                tables = page.get('tables', [])
                file_attachments.update(tables)

                # Extract images and add them to file_attachments
                images = page.get('images', [])
                file_attachments.update(images)

            # Combine all page texts into a single string
            combined_text = "\n".join(document_text)

            # Return combined text and list of unique file attachments
            return combined_text, list(file_attachments)

        except Exception as e:
            logging.error(f"Error extracting document content: {str(e)}")
            raise HTTPException(status_code=500, detail="Error extracting document content.")


if __name__ == "__main__":
    # Example usage of the query_and_evaluate_document function
    collection_name = "pdf_collection_pymupdf"
    pdf_name = "021a5339-744f-42b7-bd9b-9368b3efda7a"
    query_text = "What is the main idea of the document?"
    gpt_model = "gpt-4o-mini"
    objective = "Query"

    response = DocumentService.query_and_evaluate_document(collection_name, pdf_name, query_text, gpt_model, objective)
    print(response)
