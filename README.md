# Medical Assistant RAG

**Medical Assistant RAG** (Retrieval-Augmented Generation) is an AI-powered assistant built using trusted medical resources (Gale Encyclopedia of Medicine) and enhanced through RAG-based architecture. It enables users to retrieve accurate and comprehensible medical information via a conversational interface.

---

## Introduction

- Designed to provide reliable and accessible medical insights using a Large Language Model (LLM) and a medical knowledge base.
- Focused on general medical concepts: symptoms, conditions, procedures, and treatments.
- Provides a simple and intuitive interface for querying health-related information.

---

## Project Structure

The assistant combines various memory components and retrieval logic to generate context-aware medical responses.

### Key Components

- **User Input**: Medical query from user
- **Prompt Template**: Constructs context-rich prompts using input and history
- **Chat History**: Combines long-term and short-term memory
- **Vector Store**: Stores embedded document chunks from the knowledge base
- **LLM (Mistral AI)**: Generates final response
- **Frontend**: Built with Vue
- **Backend**: Built with Flask

---

## Tools & Frameworks

| Component         | Tool / Framework    |
|------------------|---------------------|
| Core Language     | Python              |
| Backend           | Flask               |
| Frontend          | Vue.js              |
| LLM               | Mistral AI          |
| Vector DB         | FAISS               |
| Memory Store      | SQLite              |
| RAG Pipeline      | Langchain           |

---

## Project Details

### Login System
- Flask JWT-based authentication
- Registration with username and email
- JWT-secured access for chat sessions

### Memory Design

#### Short-Term Memory
- Retains the last 4 interactions (user + assistant)
- Provides local conversational context

#### Long-Term Memory
- Summarized context of earlier chats (up to 1500 tokens)
- Enables personalized and coherent long conversations

### Query Optimization

- Rewrites follow-up questions using **Standalone Question Rewriting**
- Detects new goals or important context shifts
- Updates summaries dynamically if context relevance is detected

### Retrieval Process

- Chunks: Documents are divided into 500-token segments
- Retrieval: Top 5 chunks fetched using **Maximal Marginal Relevance (MMR)** with λ = 0.5
- Balances relevance and diversity in selected chunks

---

## Token Limits

| Input Component         | Token Limit (Max) |
|-------------------------|-------------------|
| User Query              | 900               |
| Short-Term Memory       | 6450              |
| Long-Term Memory        | 1500              |
| Retrieved Chunks        | 2500              |
| **Total Input Limit**   | **11350**         |

---

## Class Diagram


---

## API & Routes

### Auth Routes

| Method | Route            | Description                  |
|--------|------------------|------------------------------|
| POST   | `/auth/login`    | Login user                   |
| POST   | `/auth/refresh`  | Refresh JWT token            |
| POST   | `/auth/logout`   | Logout current session       |
| POST   | `/user/register` | Register a new user          |
| GET    | `/user/`         | Get user profile + chats     |

### Chat Routes

| Method | Route                     | Description                        |
|--------|---------------------------|------------------------------------|
| POST   | `/chat/new`               | Start a new chat                   |
| GET    | `/chat/{chat_id}`         | Get chat details + history         |
| POST   | `/chat/{chat_id}`         | Submit query & get assistant reply |

---

## Frontend Routes

| Route             | Component/View             | Description             |
|-------------------|----------------------------|-------------------------|
| `/login`          | `LoginView`                | User Login Page         |
| `/register`       | `RegisterView`             | User Registration Page  |
| `/chat/new`       | `MedicalAssistantView`     | Start New Chat          |
| `/chat/:chatId`   | `MedicalAssistantView`     | View Ongoing Chat       |

---

## Project Setup

### Vector DB Initialization

- Make sure knowledge documents are available in: `/vector_DB/vector_ops/documents`
- Then run:

```bash
cd backend
venv\Scripts\Activate
cd ..
cd vector_DB
python init.py
```

### Backend

```bash
cd backend
venv\Scripts\Activate
set FLASK_APP=app.py
flask run
```

### Frontend

```bash
cd frontend
npm install
npm run serve
```

---

## Project Snippets

![Architecture Diagram](https://github.com/bsrihan11/Medical-Assistant-RAG/blob/main/images/RAG_1.png)

![Architecture Diagram](https://github.com/bsrihan11/Medical-Assistant-RAG/blob/main/images/RAG_2.png)
