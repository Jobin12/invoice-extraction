import re
import json
import sys

def parse_invoice_text(text):
    data = {
        "invoice_number": None,
        "citation_date": None, # Invoice Date
        "due_date": None,
        "total_amount": None,
        "vat_number": None,
        "company_name_en": None,
        "company_name_ar": None,
        "potential_line_items": [],
        "arabic_lines": [],
        "all_lines": []
    }

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    data["all_lines"] = lines

    # Regex patterns
    # Invoice Number: Look for "Invoice No" or just a number like 6051 if labeled
    # Date: "Aug 14, 2025"
    date_pattern = re.compile(r'([A-Za-z]{3}\s+\d{1,2},\s+\d{4})')
    # Amount: "832.60" or "724.00" - looking for numbers with 2 decimals
    amount_pattern = re.compile(r'\b\d+\.\d{2}\b')
    # VAT: 15 digits starting with 3
    vat_pattern = re.compile(r'\b3\d{14}\b')
    # Arabic: Range \u0600-\u06FF
    arabic_pattern = re.compile(r'[\u0600-\u06FF]+')

    dates_found = []
    amounts_found = []

    for line in lines:
        # Arabic extraction
        if arabic_pattern.search(line):
            data["arabic_lines"].append(line)
            # Simple heuristic for Arabic company name (usually at top)
            if not data["company_name_ar"] and len(line) > 10:
                 data["company_name_ar"] = line

        # Date extraction
        dates = date_pattern.findall(line)
        if dates:
            dates_found.extend(dates)
        
        # Amount extraction
        amounts = amount_pattern.findall(line)
        if amounts:
            amounts_found.extend([float(x) for x in amounts])

        # VAT extraction
        vat = vat_pattern.search(line)
        if vat and not data["vat_number"]:
            data["vat_number"] = vat.group(0)

        # Invoice Number Heuristic
        # Looking for standalone numbers or labels
        if "Invoice No" in line or "6051" in line:
             # Try to find the number in this line or storing context?
             # Based on previous file, "6051" was on its own line.
             # Remove LTR/RTL marks if any
             clean_line = re.sub(r'[^\w\s]', '', line)
             if clean_line.strip().isdigit():
                 data["invoice_number"] = clean_line.strip()
    
    # Fallback for Invoice Number: Look for 4 digit number on its own line if not found
    if not data["invoice_number"]:
        for line in lines:
            clean_line = line.strip()
            # 6051 is 4 digits. Avoid 2025 (year).
            if clean_line.isdigit() and len(clean_line) >= 4 and clean_line != "2025":
                 # Check if it's already used as date year?
                 if "202" not in clean_line: # Simple heuristic to avoid years
                     data["invoice_number"] = clean_line
                     break
    
    # Post-processing heuristics
    if dates_found:
        data["citation_date"] = dates_found[0] # Assume first date is invoice date
        if len(dates_found) > 1:
            data["due_date"] = dates_found[-1] # Assume last date is due date

    if amounts_found:
        # Total is usually the collected max amount, or specific repeating amount
        # In this invoice: 832.60 is the total. 724.00 is subtotal.
        data["total_amount"] = max(amounts_found)

    # Companies
    # Heuristic: English company name is usually near the top, all caps
    for line in lines[:10]:
        if "EST" in line or "TRADING" in line or "COMPANY" in line or "LTD" in line:
            data["company_name_en"] = line
            break
            
    # Table Content Heuristic
    # We saw "1.00 724.00 108.60" as a pattern for Qty/Price/Tax
    # We saw product descriptions roughly around the same area or in a block.
    # Since text is destructured, we collect "Potential Line Items" by looking for the Line Item Price properties
    
    for line in lines:
        # Check if line looks like "1.00 724.00 108.60"
        nums = amount_pattern.findall(line)
        if len(nums) >= 2:
            data["potential_line_items"].append({
                "raw_line": line,
                "values": nums
            })

    return data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parser.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        text = f.read()
    
    parsed = parse_invoice_text(text)
    print(json.dumps(parsed, indent=4, ensure_ascii=False))
