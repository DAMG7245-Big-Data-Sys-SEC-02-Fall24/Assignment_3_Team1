from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidName
import logging

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)


class MongoDBHelper:
    _instances = {}

    def __new__(cls, uri: str, database_name: str):
        if cls._instances.get(database_name) is None:
            cls._instances[database_name] = super(MongoDBHelper, cls).__new__(cls)
            cls._instances[database_name]._initialized = False
        return cls._instances[database_name]

    def __init__(self, uri: str, database_name: str):
        if self._initialized:
            return
        self._initialized = True
        """
        Initialize MongoDBHelper class with connection URI and database name.
        """
        try:
            # Establish a connection to the MongoDB server
            self.client = MongoClient(uri)
            # Connect to the database
            self.database = self.client[database_name]
            logging.info(f"Successfully connected to MongoDB database: {database_name}")
        except ConnectionFailure as e:
            logging.error(f"Failed to connect to MongoDB: {str(e)}")
            raise ConnectionFailure("MongoDB connection failed")
        except InvalidName as e:
            logging.error(f"Invalid database name: {str(e)}")
            raise InvalidName("Invalid MongoDB database name")

    def get_collection(self, collection_name: str):
        """
        Get a collection from the database.
        """
        try:
            collection = self.database[collection_name]
            logging.info(f"Successfully accessed collection: {collection_name}")
            return collection
        except InvalidName as e:
            logging.error(f"Invalid collection name: {str(e)}")
            raise InvalidName("Invalid MongoDB collection name")

    def find_document_by_pdf_name(self, collection_name: str, pdf_name: str):
        """
        Find a document in a given collection by PDF name.
        """
        try:
            collection = self.get_collection(collection_name)
            document = collection.find_one({"pdf_name": pdf_name})
            if document:
                logging.info(f"Document found for pdf_name: {pdf_name}")
            else:
                logging.warning(f"No document found for pdf_name: {pdf_name}")
            return document
        except Exception as e:
            logging.error(f"An error occurred while finding the document: {str(e)}")
            raise Exception(f"An error occurred: {str(e)}")

    def find_documents_by_pdf_name(self, pdf_name: str):
        """
        Find documents across all collections by PDF name.
        """
        found_documents = []
        for collection_name in self.database.list_collection_names():
            print(collection_name)
            document = self.find_document_by_pdf_name(collection_name, pdf_name)
            if document:
                found_documents.append({"collection": collection_name, "document": document})
        return found_documents


# Factory Plugin to Handle Multiple Collections
class MongoDBFactory:
    def __init__(self, uri: str, database_name: str):
        self.db_helper = MongoDBHelper(uri, database_name)

    def get_document_by_pdf_name(self, pdf_name: str):
        """
        Search across all collections for a document with the given PDF name.
        """
        return self.db_helper.find_documents_by_pdf_name(pdf_name)


# Example usage
# if __name__ == "__main__":
#     mongo_uri = "mongodb+srv://pemmarajuv:WLAUxpGKNraNWw3h@bigdata-f24-t1.h1tab.mongodb.net/?retryWrites=true&w=majority&appName=bigdata-f24-t1"
#     factory = MongoDBFactory(uri=mongo_uri, database_name="pdf_database")
#
#     # Find documents by PDF name across collections
#     pdf_name = "7c215d46-91c7-424e-9f22-37d43ab73ea6"
#     documents = factory.get_document_by_pdf_name(pdf_name)
#     print(documents)
