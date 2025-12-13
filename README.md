# Invoice Extraction API

This project is a full-stack application for extracting structured data from PDF invoices using Google's Gemini Pro Vision model.

## Features

- **Frontend**: React-based UI for file uploads and data display.
- **Backend**: FastAPI server that handles file processing and communicates with the Gemini API.
- **AI-Powered**: Uses Gemini 1.5 Pro (or compatible) for accurate entity extraction.

## Prerequisites

- Python 3.8+
- Node.js and npm
- A Google Cloud API Key for Gemini

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Jobin12/invoice-extraction.git
cd invoice-extraction
```

### 2. Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration (.env)**:
    Create a `.env` file in the `backend` directory (you can copy the example):
    ```bash
    cp .env.example .env
    ```
    
    Open `.env` and add your Google API Key:
    ```env
    GEMINI_API_KEY=your_actual_api_key_here
    ```

5.  Run the backend server:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    The backend will run at `http://localhost:8000`.

### 3. Frontend Setup

1.  Open a new terminal and navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Start the development server:
    ```bash
    npm run dev
    ```
    The frontend will typically run at `http://localhost:5173`.

## Usage

1.  Open the frontend URL in your browser.
2.  Upload a PDF invoice.
3.  The application will send the PDF to the backend, which uses Gemini to extract structured data (Invoice Number, Date, Line Items, etc.).
4.  The extracted data will be displayed on the screen.
