import requests
from fpdf import FPDF
import os

# 1. Create a dummy PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Invoice #12345", ln=1, align="C")
pdf.cell(200, 10, txt="Amount: $500.00", ln=1, align="C")
pdf.output("test_invoice.pdf")

print("Created test_invoice.pdf")

# 2. Test Invalid File Upload
try:
    files = {'file': ('test.txt', 'This is not a pdf', 'text/plain')}
    response = requests.post('http://localhost:8000/extract', files=files)
    if response.status_code == 400:
        print("PASS: Invalid file type rejected")
    else:
        print(f"FAIL: Invalid file type not rejected (Status: {response.status_code})")
except Exception as e:
    print(f"FAIL: Error testing invalid file: {e}")

# 3. Test Valid File Upload (Expect AWS Error or Success)
# If credentials are wrong, it will be 500 or 403.
try:
    files = {'file': ('test_invoice.pdf', open('test_invoice.pdf', 'rb'), 'application/pdf')}
    response = requests.post('http://localhost:8000/extract', files=files)
    
    if response.status_code == 200:
        print("PASS: Valid PDF upload and extraction successful")
        print("Response:", response.json()['saved_file'])
        # Optional: Print raw response keys to verify structure
        if 'raw_response' in response.json():
             print("Keys found:", response.json()['raw_response'].keys())
    else:
        print(f"FAIL: Valid PDF upload failed (Status: {response.status_code})")
        print("Error:", response.text)
except Exception as e:
    print(f"FAIL: Error testing valid file: {e}")
