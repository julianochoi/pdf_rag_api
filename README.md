# PDF QA API
## Description
The PDF QA API is designed to provide question-answering capabilities over PDF documents. It allows users to upload PDF files, then query them for specific information.

The API uses a combination of text extraction, embedding generation, and vector databases to provide accurate and efficient answers.

## Features
- Upload PDF files and extract text.
  - Chunk and embed the extracted text.
  - Store the embeddings in a vector database (Chroma).
- Ask questions based on the uploaded PDF files.
  - Query the vector database to find relevant chunks based on user questions.
  - Uses an LLM to answer questions based on the retrieved chunks.
  - Displays relevant chunks retrieved to answer the question.

- Supports multiple LLM providers with fallback behavior:
  - OpenAI
  - Groq
  - Google
  - Anthropic

- Frontend(Streamlit) for easy interaction with the API.

- Fully dockerized environment for easy deployment.
- API documentation using OpenAPI.

## Requirements
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Usage
The simplest way to run the application is to use Docker Compose. This will set up all the necessary services, including the API, database, and any other dependencies.

Steps to run the application:
1. Clone the repository
1. Setup your LLM provider [credentials](#llm-provider-configuration) at `backend/llm_provider.yaml` file.
1. Run the compose command to start the application:
  > Note: For the first time running the application, it might take a while to build all the images and download the embedding models.
  ```bash
  docker-compose up -d
  ```
1. Wait for the containers to start. You can check the logs using:
  ```bash
  docker-compose logs -f
  ```
1. Once the containers are up and running, you can access the application at:
  - Streamlit Frontend: http://localhost:8501
  - API Docs: http://localhost:5000/docs

## Configuration
### Backend
1. Update the `backend/llm_provider.yaml` file with your [provider details](#llm-provider-configuration).
1. (Optional) Create a file `.env` inside `backend` directory.
  - Update the `.env` file with your [configuration details](#backend-environment-variables), if necessary.

#### LLM Provider Configuration
The application supports multiple LLM providers and uses a fallback mechanism to switch between them if one fails. The priority order is defined from top to bottom in the yaml file.
```yaml
llms:
  - name: "<name of your choice>"
    provider: "one of google, openai, anthropic, groq"
    model: "<model name>"
    api_key: "<api key>"
```

<details>
<summary>Config file example</summary>

```yaml
llms:
  - name: "primary-google"
    provider: "google"
    model: "gemma3"
    api_key: "<google aistudio api key>"
  - name: "fallback"
    provider: "openai"
    model: "gpt-3.5-turbo"
    api_key: "<openai api key>"
```

</details>

#### Backend Environment Variables
Below is a table of the available environment variables and their default values.
<details>
<summary>Environment variables</summary>

|Variable				|Description							|Default Value		|
|:---					|:---									|:---:				|
|ENVIRONMENT			|Deploy environment (dev, prod, etc.)	|"dev"				|
|PORT					|-										|5000				|
|LOG_LEVEL				|-										|"DEBUG"			|
|CORRELATION_ID_HEADER	|Correlation header used for tracing.	|"X-Request-ID"		|
|EMBEDDING_MODEL		|Model used to compute embeddings.		|"all-MiniLM-L6-v2"	|
|CHROMA_HOST			|URI to Chroma DB host.					|"chromadb"			|
|CHROMA_PORT			|-										|8000				|
|CHROMA_COLLECTION		|-										|"pdf_chunks"		|
</details>

### Frontend
1. (Optional) Create a file `.env` inside `frontend` directory.
  - Update the `.env` file with your [configuration details](#environment-variables), if necessary.

#### Frontend Environment Variables
Below is a table of the available environment variables and their default values.
<details>
<summary>Environment variables</summary>

|Variable	|Description|Default Value			|
|:---		|:---		|:---:					|
|BACKEND_URL|-			|"http://backend:5000"	|

