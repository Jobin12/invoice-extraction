import os
import json
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GENAI_API_KEY)

# Use Gemini 2.5 Pro
MODEL_NAME = "gemini-2.5-pro"

def upload_to_gemini(file_content, mime_type="application/pdf"):
    """
    Uploads the file content to Gemini. 
    Note: For the python SDK, we usually upload files using the File API for large context.
    However, for immediate turning, we can pass the bytes directly in some versions, 
    but utilizing the parts structure is safer.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    return model

@app.get("/")
def read_root():
    return {"message": "Invoice Extraction API (Gemini) is running."}

@app.post("/extract")
async def extract_invoice_data(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read file
        file_content = await file.read()
        
        # Initialize Model
        model = genai.GenerativeModel(MODEL_NAME)

        # Prompt for structured JSON
        prompt = """
        Extract the data from this invoice PDF into the following strict JSON format. 
        If a field is not found, return null (or "N/A" for text fields).
        
        REQUIRED JSON SCHEMA:
        {
            "invoice_number": "string",
            "invoice_date": "string",
            "due_date": "string",
            "seller": {
                "name_english": "string",
                "name_arabic": "string",
                "address": "string",
                "vat_number": "string",
                "cr_number": "string"
            },
            "buyer": {
                "name": "string",
                "address": "string",
                "vat_number": "string"
            },
            "line_items": [
                {
                    "description": "string",
                    "quantity": "number/string",
                    "unit_price": "number/string",
                    "total": "number/string"
                }
            ],
            "totals": {
                "subtotal": "string",
                "vat_amount": "string",
                "grand_total": "string"
            },
            "bank_details": {
                "bank_name": "string",
                "account_number": "string",
                "iban": "string"
            }
        }
        
        Ensure "totals" and "bank_details" keys exactly match the names above if data exists.
        Return ONLY valid JSON.
        """

        # Generate content
        # Pass part with mime_type
        response = model.generate_content(
            [
                {"mime_type": "application/pdf", "data": file_content},
                prompt
            ]
        )
        
        # Parse JSON from response text
        # Gemini might wrap in ```json ... ```
        raw_text = response.text
        cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
        
        try:
            json_response = json.loads(cleaned_text)
        except json.JSONDecodeError:
            # Fallback if valid JSON wasn't returned, just return text wrapped
            json_response = {"raw_text_output": raw_text}

        # Save raw response
        os.makedirs("responses", exist_ok=True)
        filename = f"responses/{file.filename}.json"
        with open(filename, "w") as f:
            json.dump(json_response, f, indent=4, ensure_ascii=False)
            
        return {
            "message": "Extraction successful", 
            "saved_file": filename,
            "raw_response": json_response
        }
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
