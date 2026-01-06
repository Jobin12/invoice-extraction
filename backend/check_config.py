from dotenv import load_dotenv, find_dotenv
import os

# Try to find the .env file
dotenv_path = find_dotenv()
print(f"Found .env at: {dotenv_path}")

# Load it
load_dotenv(dotenv_path)

# Check specific keys
keys = ["GEMINI_API_KEY", "ZOHO_CLIENT_ID", "ZOHO_CLIENT_SECRET", "ZOHO_REFRESH_TOKEN", "ZOHO_ORG_ID", "ZOHO_DC"]

print("\n--- Environment Variable Check ---")
for key in keys:
    val = os.getenv(key)
    if val is None:
        print(f"❌ {key}: MISSING")
    else:
        masked = val[:4] + "..." if len(val) > 4 else "***"
        print(f"✅ {key}: Found (Value starts with: '{masked}', Length: {len(val)})")
        
print("\n--- DC Check ---")
print(f"ZOHO_DC raw value: '{os.getenv('ZOHO_DC')}'")
