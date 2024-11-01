# Assignment 3 - MultiModal Rag Application

## Project Links and Resources

- **GitHub Issues and Tasks**: [Link to GitHub Project Issues](https://github.com/orgs/DAMG7245-Big-Data-Sys-SEC-02-Fall24/projects/5/views/1)
- **Codelabs Documentation**: [Link to Codelabs](https://codelabs-preview.appspot.com/?file_id=1-QWsYzlHKrLpZkAiQ0VeiFPaY5uey8HvwCgqSWxd244#0)
- **Project Submission Video (5 Minutes)**: [Link to Submission Video](https://drive.google.com/drive/folders/1wgYeUY-HsDuWcqGq1hSNVRQ3gvQBMLZC)
- **Hosted Application Links**:
  - **Frontend (Streamlit)**: [Link to Streamlit Application](http://35.185.111.184:8501)
  - **Backend (FastAPI)**: [Link to FastAPI Application](http://35.185.111.184:8000/docs)
  - **Data Processing Service (Airflow)**: [Link to Data Processing Service](http://35.185.111.184:8080)
---
![Architecture Diagram](assets/A3_architecture%20diagram.jpeg)
## Introduction

This project focuses on establishing a comprehensive multimodal Retrieval-Augmented Generation (RAG) pipeline, specifically for extracting, storing, and processing financial documents from the CFA Institute Research Foundation. The system is designed to efficiently handle various document formats and create a streamlined experience for querying and summarizing documents.

### Key Technologies:

- **Llama Parse Framework** for initial data extraction and parsing.
- **PyMuPDF** for PDF text extraction in the QA and summarization API.
- **FastAPI** for backend processing, including JWT-based authentication and API handling.
- **Streamlit** for frontend interface enabling user interaction with processed data.
- **Apache Airflow** for automating data ingestion and orchestration.
- **AWS S3** for storing scraped images and PDFs.
- **Snowflake** for database management and indexing extracted document data.
- **MongoDB** for storing extracted data from the PDF documents.
- **PostgreSQL** for managing user credentials securely.

The project also utilizes JWT tokens for secure API endpoint interactions, supporting access and refresh tokens for effective session management.

## Problem Statement

The project's primary objective is to develop an automated pipeline to ingest, process, and interact with financial research documents. Users are provided with a secure platform that allows efficient querying and summarization of documents, leveraging advanced processing tools and natural language models to facilitate interactive document exploration.

### Key Objectives

1. **Automated Data Ingestion**: Efficiently scrape document data, including images, text, and PDFs, and store it in a structured format.
2. **Streamlined Query and Summarization**: Provide advanced querying and summarization using OpenAI models and multimodal RAG capabilities.
3. **Secure User Management**: Ensure robust access management with JWT-based authentication.
4. **Scalable Infrastructure**: Enable cloud-based deployment to handle extensive datasets and multiple document types.
   

### Part 1: Data Ingestion and Database Population

- **Airflow Orchestration**: Set up automated pipelines in Airflow for scraping and processing publication data.
- **Text Extraction**: Implement pipelines to extract data using:
  - **Open-source** tool: PyMuPDF.
  - **Enterprise API**: Llama Parse framework.
- **Data Storage**: Store extracted data in AWS S3, ensuring secure access and retrieval from Snowflake for database indexing and organization.

### Part 2: Client-Facing Application Development

#### Backend (FastAPI)

- **User Authentication**:
  - Implement JWT-based login and registration.
  - Require JWT bearer tokens for all endpoints.
  - Implement access and refresh token mechanisms for session management.
  
- **RAG Application**:
  - Use PyMuPDF for document summarization and querying in QA.
  - Integrate Llama Parse framework for robust report generation.
  - 

#### Frontend (Streamlit)

- **User Interaction**:
  - Provide a streamlined interface for user registration and login.
  - Enable document querying and summarization through interactive options.
  - Display selected PDF extracts with query-specific information.

### Deployment

- **Dockerized Deployment**:
  - Use Docker Compose to deploy the backend (FastAPI) and frontend (Streamlit) on GCP, with Docker images compatible with both ARM and AMD architectures.
  - Ensure `.env` and `secrets` directories are properly configured for deployment.


## Local Setup and Running the Project Locally

### Prerequisites

Ensure the following tools are installed on your system:

- **Python 3.12**
- **Poetry** for dependency management
- **Docker** and **Docker Compose**
- **Git** for repository management

### Clone the Repository

Clone the repository to your local machine:


git clone https://github.com/DAMG7245-Big-Data-Sys-SEC-02-Fall24/Assignment2_team1.git
cd Assignment2_team1

### Part 2: Client-Facing Application Development
#### FastAPI
- [ ] Implement user registration and login functionality.
- [ ] Secure application using JWT authentication:
  - [ ] Protect all endpoints except for registration and login.
  - [ ] Ensure JWT token is required for accessing protected endpoints.
  - [ ] Indicate protected endpoints with padlock icon in Swagger UI.
- [ ] Use a SQL database for storing user credentials with hashed passwords.
- [ ] Move business logic to a FastAPI backend service.
- [ ] Define services to be invoked through Streamlit.

#### Streamlit
- [ ] Develop user-friendly registration and login page.
- [ ] Implement Question Answering interface for authenticated users.
- [ ] Enable selection from a variety of preprocessed PDF extracts.
- [ ] Ensure the system can query specific PDFs upon selection.

### Deployment
- [ ] Containerize FastAPI and Streamlit applications using Docker Compose.
- [ ] Deploy applications to a public cloud platform.
- [ ] Ensure deployed applications are publicly accessible for seamless user interaction.

### Submission
- [ ] Fully functional Airflow pipelines, Streamlit application, and FastAPI backend.
- [ ] Ensure all services are deployed and publicly accessible with documentation.
- [ ] Include the following in the GitHub repository:
  - [ ] Project summary, research, PoC, and other information.
  - [ ] GitHub project issues and tasks.
  - [ ] Diagrams explaining the architecture and flow.
  - [ ] Fully documented Codelabs document.
  - [ ] 5-minute video of the project submission.
  - [ ] Link to hosted applications, backend, and data processing services.

### Desired Outcome:
- Secure extraction of PDF data.
- Efficient querying and summarization of documents.
- Scalable and user-friendly infrastructure for deployment.

### Constraints:
- Handling large datasets (PDFs from the GAIA dataset).
- Managing multiple APIs for extraction (open-source and closed-source).
- Ensuring security with JWT-based authentication.

## Proof of Concept

The project uses two main technologies for PDF extraction:
- **PyMuPDF** (open-source) and **PDF.co** (closed-source) APIs.
  
The extracted data is stored in GCP and MongoDB for easy querying and further processing. Initial setup involved:
- Setting up Airflow for automating the extraction process.
- Configuring MongoDB to store document metadata and extracted text.
- Implementing FastAPI for backend functionalities and integrating OpenAI's GPT models for summarization and querying.

Challenges such as managing API limits and optimizing extraction pipelines have been addressed by caching results and using efficient database queries.

Certainly! Here’s the section for **local setup and running the code locally** that you can insert into your existing README:

---

## Local Setup and Running the Project Locally

### Prerequisites

Ensure that the following dependencies are installed on your system:

- **Python 3.12** or later
- **Poetry** for dependency management
- **Docker** and **Docker Compose**
- **Git** for cloning the repository

### Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/DAMG7245-Big-Data-Sys-SEC-02-Fall24/Assignment2_team1.git
cd Assignment2_team1
```

### Backend Setup

1. Navigate to the `backend` directory:

   ```bash
   cd backend
   ```

2. Install the dependencies using Poetry:

   ```bash
   poetry install
   ```

3. Set up environment variables by creating a `.env` file in the `backend` directory (refer to the **Environment Variables** section for more details).

4. Run the backend server:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The backend will be accessible at `http://localhost:8000`.

### Frontend Setup

1. Navigate to the `frontend` directory:

   ```bash
   cd ../frontend
   ```

2. Install the dependencies using Poetry:

   ```bash
   poetry install
   ```

3. Set up environment variables by creating a `.env` file in the `frontend` directory (refer to the **Environment Variables** section for more details).

4. Run the frontend server:

   ```bash
   streamlit run main.py --server.port=8501 --server.address=0.0.0.0
   ```

   The frontend will be accessible at `http://localhost:8501`.

### Running Both Services

To run the entire project locally:

1. Open two terminal windows or tabs.
2. In the first terminal, navigate to the `backend` directory and start the backend service.
3. In the second terminal, navigate to the `frontend` directory and start the frontend service.


## Project Directory Structure

Here is the complete directory structure of the project:

```
(base) udaykiran@Udays-MacBook-Pro Assignment_3_Team1 % tree 
.
├── README.md
├── airflow
│   ├── Dockerfile
│   ├── dags
│   │   ├── __pycache__
│   │   │   └── scraper_dag.cpython-37.pyc
│   │   ├── publications_data.csv
│   │   ├── scraper_dag.py
│   │   └── scripts
│   │       ├── __init__.py
│   │       ├── __pycache__
│   │       │   ├── __init__.cpython-37.pyc
│   │       │   ├── aws_s3.cpython-37.pyc
│   │       │   ├── scraper.cpython-37.pyc
│   │       │   └── snowflake_utils.cpython-37.pyc
│   │       ├── aws_s3.py
│   │       ├── scraper.py
│   │       └── snowflake_utils.py
│   ├── docker-compose.yaml
│   ├── plugins
│   ├── readme.md
│   ├── requirements.txt
│   └── variables.json
├── airflow_var
│   ├── Dockerfile
│   ├── dags
│   │   ├── __pycache__
│   │   │   └── scraper_dag.cpython-37.pyc
│   │   ├── publications_data.csv
│   │   ├── scraper_dag.py
│   │   └── scripts
│   │       ├── __init__.py
│   │       ├── __pycache__
│   │       │   ├── __init__.cpython-37.pyc
│   │       │   ├── aws_s3.cpython-37.pyc
│   │       │   ├── scraper.cpython-37.pyc
│   │       │   └── snowflake_utils.cpython-37.pyc
│   │       ├── aws_s3.py
│   │       ├── scraper.py
│   │       └── snowflake_utils.py
│   ├── docker-compose.yaml
│   ├── plugins
│   ├── readme.md
│   ├── requirements.txt
│   └── variables.json
├── assets
│   ├── A3_architecture diagram.jpeg
│   └── Backend API.jpeg
├── backend
│   ├── Dockerfile
│   ├── __init__.py
│   ├── app
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   └── main.cpython-312.pyc
│   │   ├── config
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   └── settings.cpython-312.pyc
│   │   │   └── settings.py
│   │   ├── controllers
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   └── auth_controller.cpython-312.pyc
│   │   │   └── auth_controller.py
│   │   ├── main.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── publication.cpython-312.pyc
│   │   │   │   └── user_model.cpython-312.pyc
│   │   │   ├── publication.py
│   │   │   └── user_model.py
│   │   ├── routes
│   │   │   ├── __pycache__
│   │   │   │   ├── auth_routes.cpython-312.pyc
│   │   │   │   ├── publications_routes.cpython-312.pyc
│   │   │   │   ├── rag.cpython-312.pyc
│   │   │   │   └── summary_routes.cpython-312.pyc
│   │   │   ├── auth_routes.py
│   │   │   ├── publications_routes.py
│   │   │   ├── rag.py
│   │   │   └── summary_routes.py
│   │   └── services
│   │       ├── PublicationService.py
│   │       ├── __init__.py
│   │       ├── __pycache__
│   │       │   ├── PublicationService.cpython-312.pyc
│   │       │   ├── __init__.cpython-312.pyc
│   │       │   ├── auth_service.cpython-312.pyc
│   │       │   ├── database_service.cpython-312.pyc
│   │       │   ├── document_service.cpython-312.pyc
│   │       │   ├── gpt.cpython-312.pyc
│   │       │   ├── mongo.cpython-312.pyc
│   │       │   ├── snowflake.cpython-312.pyc
│   │       │   └── tools.cpython-312.pyc
│   │       ├── auth_service.py
│   │       ├── database_service.py
│   │       ├── document_service.py
│   │       ├── gpt.py
│   │       ├── mongo.py
│   │       ├── object_store.py
│   │       ├── snowflake.py
│   │       ├── table_page_1_1.csv
│   │       └── tools.py
│   ├── multimodal_report_generation.ipynb
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── secrets
│       ├── gcp.json
│       ├── private_key.pem
│       └── public_key.pem
├── docker-compose.yaml
├── env
├── frontend
│   ├── Dockerfile
│   ├── app.py
│   ├── app_pages
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── document_actions_page.cpython-312.pyc
│   │   │   ├── documents_page.cpython-312.pyc
│   │   │   ├── home.cpython-312.pyc
│   │   │   ├── home_page.cpython-312.pyc
│   │   │   └── pdf_gallery.cpython-312.pyc
│   │   ├── document_actions_page.py
│   │   ├── documents_page.py
│   │   ├── home_page.py
│   │   └── pdf_gallery.py
│   ├── components
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   └── __init__.cpython-312.pyc
│   │   ├── navbar.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── pdf_viewer.cpython-312.pyc
│   │   │   │   └── s3_service.cpython-312.pyc
│   │   │   ├── pdf_viewer.py
│   │   │   └── s3_service.py
│   │   └── ui
│   │       ├── __init__.py
│   │       ├── __pycache__
│   │       │   ├── __init__.cpython-312.pyc
│   │       │   ├── buttons.cpython-312.pyc
│   │       │   └── card.cpython-312.pyc
│   │       ├── buttons.py
│   │       └── card.py
│   ├── poetry.lock
│   ├── pyproject.toml
│   ├── services
│   │   ├── __pycache__
│   │   │   ├── authentication.cpython-312.pyc
│   │   │   ├── session_store.cpython-312.pyc
│   │   │   └── utils.cpython-312.pyc
│   │   ├── authentication.py
│   │   ├── pdf_viewer.py
│   │   ├── session_store.py
│   │   └── utils.py
│   └── styles
│       └── styles.css
├── infra
│   ├── provider.tf
│   └── s3.tf
├── prototyping
│   └── __init__.py
├── scripts
│   └── __init__.py
├── secrets
│   ├── gcp.json
│   ├── private_key.pem
│   └── public_key.pem
└── sql
    └── schema.sql

```

### Directory Descriptions:

- **`airflow_pipelines`**:
  Contains the DAGs (Directed Acyclic Graphs) for orchestrating the extraction pipeline using Airflow. These DAGs define the tasks to be executed in sequence for text extraction, storing data, and performing other ETL processes.

- **`backend`**:
  - `app`: Houses the FastAPI backend which includes authentication, document querying, and summarization services.
  - `config`: Contains configuration settings for the backend such as environment variables and database connection.
  - `controllers`: Implements the logic for user authentication.
  - `routes`: Manages the API endpoints for authentication, document querying, and summarization.
  - `services`: Core services for handling business logic, database interactions, and API calls to GPT models and MongoDB.
  - `Dockerfile`: Configuration to build the backend FastAPI Docker container.
  - `pyproject.toml`: Python dependencies for the backend.

- **`frontend`**:
  - Contains the Streamlit frontend which interacts with the backend to allow users to select, query, and summarize documents.
  - `services`: Includes the logic for interacting with GCP for file storage and authentication handling.
  - `Dockerfile`: Configuration to build the frontend Streamlit Docker container.
  - `pyproject.toml`: Python dependencies for the frontend.

- **`infra`**:
  Infrastructure setup for the project using Terraform. This includes:
  - GCP resource definitions (storage buckets, VMs, PostgreSQL, etc.).
  - Security configurations such as firewalls and SSH keys.
  - `sql.tf`: Defines the setup for the PostgreSQL database in GCP.

- **`prototyping`**:
  Contains various scripts and notebooks used during the development and testing phase of the project for different PDF extraction methods and database connections.

- **`sql`**:
  Defines the SQL schema for the PostgreSQL database, including the Users table for authentication.

## Architecture Diagram

![Architecture Diagram](assets/airflow_architecture_diagram.png)
![High Level Diagram](assets/high_level_architecture_diagram_1.png)

### Description of Components:
- **Airflow**: Orchestrates the ETL pipeline for extracting PDF text and storing it in MongoDB.
- **FastAPI**: Handles user registration, authentication, and requests to process and query the extracted data.
- **Streamlit**: The client-facing frontend where users can select documents, summarize them, or query specific content.
- **MongoDB**: Stores the extracted text and metadata.
- **PostgreSQL**: Stores user information for authentication.
- **GCP (Google Cloud Platform)**: Provides the infrastructure for the entire platform, including storage (GCS) and VM instances for deployment.
- **OpenAI GPT Models**: Used for querying and summarization of document content.

### Data Flow:
1. PDFs are uploaded to GCP storage.
2. Airflow pipelines extract text using open-source or closed-source tools.
3. Extracted data is stored in MongoDB and GCP for further processing.
4. Users interact with the data through the Streamlit frontend, querying and summarizing the documents.

### Challenges Faced:
- **API Rate Limits**: Handled by caching results and optimizing request frequency.
- **Large File Handling**: Implemented efficient streaming methods for large PDFs.
- **Authentication**: Secured the API endpoints using JWT tokens to prevent unauthorized access.



**Team Members:**
- Uday Kiran Dasari - Backend ,Docker, Fronted - 33.3%
- Sai Surya Madhav Rebbapragada - Backend, Frontend, Integratrion - 33.3%
- Akash Varun Pennamaraju - Airflow, Infra setup - 33.3%


## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Airflow Documentation](https://airflow.apache.org/docs/)
- [OpenAI GPT API](https://platform.openai.com/docs/)
- [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/)
- [Google Cloud Storage](https://cloud.google.com/storage/docs/)

