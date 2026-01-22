# IKMS-STEMLink(Planner Agent)

A sophisticated Multi-Agent Retrieval-Augmented Generation (RAG) system built with FastAPI, LangChain, and LangGraph. This system provides intelligent question-answering capabilities over indexed PDF documents using a multi-agent orchestration pipeline.

## 🚀 Deployment

### 🧠 Backend
- **API:** https://ikms-stemlink-production.up.railway.app



### 🌐 Frontend
- **Live App:** https://ikms-chat-bot.vercel.app

  
## 🚀 Features


### Core Capabilities
- **Multi-Agent RAG Pipeline**: Four specialized agents working in sequence to provide accurate, verified answers
- **PDF Document Indexing**: Upload and index PDF documents into a vector database for semantic search
- **Session-Based Conversations**: Maintain conversation context across multiple interactions
- **Intelligent Question Planning**: Automatically decomposes complex questions into focused sub-queries
- **Context-Aware Retrieval**: Retrieves relevant document chunks based on semantic similarity
- **Answer Verification**: Multi-stage verification to eliminate hallucinations and ensure accuracy

### Technical Highlights
- **FastAPI REST API**: Modern, async API with comprehensive error handling
- **LangGraph Orchestration**: Stateful agent workflow management
- **Pinecone Vector Store**: Scalable vector database for document embeddings
- **Supabase Storage**: Cloud storage for uploaded PDF files
- **OpenAI Integration**: GPT-4o-mini for reasoning and text-embedding-3-small for embeddings

## 📋 Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Multi-Agent Pipeline](#multi-agent-pipeline)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Usage Examples](#usage-examples)

## 🏗️ Architecture

### System Overview

The system follows a multi-agent architecture where specialized agents collaborate to answer questions:

```
User Question
    ↓
[Planner Agent] → Decomposes question into sub-queries and search plan
    ↓
[Retrieval Agent] → Searches vector database using retrieval tool
    ↓
[Summarization Agent] → Generates draft answer from retrieved context
    ↓
[Verification Agent] → Verifies and corrects the answer
    ↓
Final Verified Answer
```

### Components

1. **API Layer** (`src/app/api.py`): FastAPI endpoints for QA and document indexing
2. **Service Layer** (`src/app/services/`): Business logic for QA and indexing operations
3. **Agent Layer** (`src/app/core/agents/`): Multi-agent orchestration using LangGraph
4. **Retrieval Layer** (`src/app/core/retrieval/`): Vector store integration and document retrieval
5. **Storage Layer** (`src/app/core/storage/`): File upload and Supabase integration
6. **LLM Layer** (`src/app/core/llm/`): OpenAI model factory and configuration

## 🔧 Installation

### Prerequisites

- Python >= 3.11
- UV package manager (recommended) or pip
- Pinecone account and API key
- OpenAI API key
- Supabase account (for file storage)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd IKMS-STEMLink
   ```

2. **Install dependencies**
   
   Using UV (recommended):
   ```bash
   uv sync
   ```
   
   Using pip:
   ```bash
   pip install -e .
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL_NAME=gpt-4o-mini
   OPENAI_EMBEDDING_MODEL_NAME=text-embedding-3-small
   
   # Pinecone Configuration
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=your_index_name
   
   # Supabase Configuration
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   BUCKET_NAME=your_bucket_name
   
   # CORS Configuration
   ALLOWED_ORIGIN=http://localhost:3000
   
   # Retrieval Configuration
   RETRIEVAL_K=4
   ```

4. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `https://ikms-stemlink-production.up.railway.app`

## ⚙️ Configuration

Configuration is managed through environment variables and Pydantic Settings. Key settings include:

- **OpenAI**: Model selection and API key
- **Pinecone**: Vector database connection and index name
- **Supabase**: Storage bucket configuration
- **CORS**: Allowed origins for API access
- **Retrieval**: Number of document chunks to retrieve (default: 4)

All settings are loaded from environment variables via `src/app/core/config.py`.

## 📡 API Endpoints

### 1. Health Check
```
GET https://ikms-stemlink-production.up.railway.app
```
Returns a welcome message.

### 2. Question Answering
```
POST https://ikms-stemlink-production.up.railway.app/qa
```

**Request Body:**
```json
{
  "question": "What are the advantages of vector databases?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "answer": "Final verified answer...",
  "context": "Retrieved context chunks...",
  "plan": "1. Search for advantages...",
  "sub_questions": ["vector database advantages", "..."],
  "session_id": "session-uuid"
}
```

### 3. PDF Indexing
```
POST https://ikms-stemlink-production.up.railway.app/index-pdf
```

**Request:** Multipart form data with PDF file

**Response:**
```json
{
  "filename": "timestamp_filename.pdf",
  "chunks_indexed": 42,
  "message": "PDF indexed successfully."
}
```

## 🤖 Multi-Agent Pipeline

### Agent Roles

#### 1. Planner Agent
- **Purpose**: Analyzes and decomposes user questions
- **Responsibilities**:
  - Identifies ambiguities and key entities
  - Breaks down complex questions into focused sub-questions
  - Generates structured search plans
  - Optimizes queries for information retrieval

#### 2. Retrieval Agent
- **Purpose**: Gathers relevant context from vector database
- **Tools**: `retrieval_tool` - Searches Pinecone vector store
- **Responsibilities**:
  - Executes semantic search using sub-questions
  - Retrieves top-k relevant document chunks
  - Consolidates context from multiple queries
  - Formats context with page references

#### 3. Summarization Agent
- **Purpose**: Generates draft answers from retrieved context
- **Responsibilities**:
  - Synthesizes information from context chunks
  - Creates coherent, context-grounded answers
  - Explicitly states when information is insufficient
  - Avoids hallucination by using only provided context

#### 4. Verification Agent
- **Purpose**: Verifies and corrects draft answers
- **Responsibilities**:
  - Cross-references draft answer with original context
  - Removes unsupported claims
  - Ensures factual accuracy
  - Produces final verified answer

### State Management

The pipeline uses LangGraph's state management with `QAState`:
- **question**: Original user question
- **plan**: Structured search plan from planner
- **sub_questions**: List of decomposed sub-queries
- **context**: Retrieved document chunks
- **draft_answer**: Initial answer from summarization
- **answer**: Final verified answer
- **messages**: Conversation history for session continuity

## 📁 Project Structure

```
IKMS-STEMLink/
├── main.py                      # FastAPI application entry point
├── pyproject.toml               # Project dependencies and metadata
├── README.md                    # This file
│
└── src/
    └── app/
        ├── __init__.py
        ├── api.py               # API routes and endpoints
        ├── models.py            # Pydantic request/response models
        │
        ├── core/
        │   ├── config.py        # Settings and configuration
        │   │
        │   ├── agents/
        │   │   ├── agents.py    # Agent node implementations
        │   │   ├── graph.py     # LangGraph orchestration
        │   │   ├── prompts.py   # Agent system prompts
        │   │   ├── state.py     # State schema definition
        │   │   └── tools.py     # Agent tools (retrieval)
        │   │
        │   ├── llm/
        │   │   └── factory.py   # LLM instance factory
        │   │
        │   ├── retrieval/
        │   │   ├── vectore_store.py    # Pinecone integration
        │   │   └── serialization.py    # Document chunk formatting
        │   │
        │   └── storage/
        │       ├── connection.py       # Supabase client
        │       └── upload_file.py      # File upload handler
        │
        └── services/
            ├── qa_service.py     # QA service layer
            └── indexing_service.py  # Document indexing service
```

## 📦 Dependencies

### Core Framework
- **fastapi** (>=0.124.0): Modern web framework
- **uvicorn** (>=0.38.0): ASGI server

### LangChain Ecosystem
- **langchain** (>=1.1.2): Core LangChain framework
- **langchain-community** (>=0.3.0): Community integrations
- **langchain-openai** (>=1.1.0): OpenAI integration
- **langchain-pinecone** (>=0.2.13): Pinecone vector store
- **langchain-text-splitters** (>=1.0.0): Document text splitting
- **langgraph** (>=1.0.4): Multi-agent orchestration

### Vector Database & Storage
- **pinecone-client** (>=6.0.0): Pinecone SDK
- **supabase** (>=2.27.2): Supabase client

### Utilities
- **pydantic-settings** (>=2.0.0): Settings management
- **pypdf** (>=6.4.1): PDF document loading
- **python-dotenv** (>=1.2.1): Environment variable loading
- **python-multipart** (>=0.0.20): File upload support

## 💡 Usage Examples

### Index a PDF Document

```bash
curl -X POST "https://ikms-stemlink-production.up.railway.app/index-pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### Ask a Question

```bash
curl -X POST "https://ikms-stemlink-production.up.railway.app/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main advantages of vector databases?",
    "session_id": "user-session-123"
  }'
```

### Continue a Conversation

```bash
# First question
curl -X POST "https://ikms-stemlink-production.up.railway.app/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is a vector database?",
    "session_id": "session-123"
  }'

# Follow-up question (uses conversation history)
curl -X POST "https://ikms-stemlink-production.up.railway.app/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does it differ from traditional databases?",
    "session_id": "session-123"
  }'
```

## 🔒 Security & Best Practices

- **API Keys**: Store all API keys in environment variables, never commit them
- **CORS**: Configure `ALLOWED_ORIGIN` appropriately for production
- **Error Handling**: Comprehensive exception handling with proper HTTP status codes
- **File Validation**: PDF-only uploads with content-type validation
- **Session Management**: Thread-based session management via LangGraph checkpointer




---

**Note**: This is a demo system for multi-agent RAG capabilities. Ensure proper configuration of all external services (OpenAI, Pinecone, Supabase) before deployment.

