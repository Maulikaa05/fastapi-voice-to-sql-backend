# FastAPI Voice-to-SQL Backend

A powerful AI-powered backend that converts voice input into SQL queries and returns intelligent, summarized results. Built with FastAPI, OpenAI, ChromaDB, and Google Speech Recognition.

---

## Features

Voice Transcription: Upload audio files and get them transcribed to text using Google Speech Recognition.

Natural Language to SQL: Converts plain English (or voice) queries into SQL using OpenAI + ChromaDB vector search.

MySQL Integration: Executes generated SQL queries against a MySQL database (via XAMPP).

AI Summarization: Summarizes database results into human-readable responses using OpenAI.

Smart Date Handling: Automatically resolves relative date expressions (e.g., "first week of April") to real dates.

REST API: Clean, documented API endpoints built with FastAPI.

Cloud Ready: Deployable on Render with render.yaml included.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | Web framework & API server |
| OpenAI API | Natural language to SQL generation and result summarization |
| ChromaDB | Vector store for schema-aware SQL generation |
| SpeechRecognition | Audio-to-text transcription (Google Speech API) |
| Pydub | Audio file conversion and preprocessing |
| MySQL (XAMPP) | Database backend |
| Uvicorn | ASGI server |
| python-dotenv | Environment variable management |

---

## Project Structure

```
fastapi-voice-to-sql-backend/
|-- main.py                  # FastAPI app, API endpoints
|-- sql_generator.py         # NLP to SQL logic using OpenAI + ChromaDB
|-- openai_helper.py         # OpenAI API utilities (summarization)
|-- xampp.py                 # MySQL database connection and query execution
|-- store_schema_chunks.py   # Stores DB schema into ChromaDB vector store
|-- config.py                # Configuration settings
|-- static/                  # Frontend static files
|-- chroma_db/               # ChromaDB persistent vector store
|-- requirements.txt         # Python dependencies
|-- render.yaml              # Render.com deployment config
```

---

## Setup and Installation

### Prerequisites
Python 3.9+ or higher.
XAMPP with MySQL running locally.
OpenAI API Key configured.
FFmpeg installed (required by Pydub for audio conversion).

### Step 1: Clone the Repository
```
git clone https://github.com/Maulikaa05/fastapi-voice-to-sql-backend.git
cd fastapi-voice-to-sql-backend
```

### Step 2: Create a Virtual Environment
```
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a .env file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key_here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=your_database_name
```

### Step 5: Initialize the Vector Store
```
python store_schema_chunks.py
```

### Step 6: Run the Server
```
uvicorn main:app --reload
```

The API will be available at: http://localhost:8000

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Serves the frontend UI |
| POST | /transcribe-voice/ | Converts audio file to text |
| POST | /process-text/ | Converts text to SQL, runs query, returns summary |

### POST /transcribe-voice/
Accepts an audio file and returns the transcribed text.

Request format: multipart/form-data with field file (audio file)

Response format:
```
{
  "success": true,
  "text": "Show me all events in April"
}
```

### POST /process-text/
Converts natural language to SQL, executes the query, and returns summarized results.

Request format: form field text (natural language query)

Response format:
```
{
  "success": true,
  "query": "SELECT * FROM events WHERE ...",
  "results": [...],
  "summary": "Found 5 events in April 2026..."
}
```

---

## Deployment on Render

This project includes render.yaml for easy deployment on Render.com.

Step 1: Push your code to GitHub.
Step 2: Connect your repository to Render.
Step 3: Set your environment variables in the Render dashboard.
Step 4: Render will auto-deploy using the render.yaml configuration.

---

## Dependencies

```
fastapi
uvicorn
openai
pydub
speechrecognition
pyttsx3
python-dotenv
mysql-connector-python
chromadb
python-multipart
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

First, fork the repository.
Second, create your feature branch: git checkout -b feature/AmazingFeature.
Third, commit your changes: git commit -m 'Add some AmazingFeature'.
Fourth, push to the branch: git push origin feature/AmazingFeature.
Fifth, open a Pull Request.

---

## License

This project is open source and available under the MIT License.

---

Built with FastAPI and OpenAI
