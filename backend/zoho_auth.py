import requests
import argparse
import sys

# Zoho Accounts URL
# Note: This might vary based on data center (e.g., .com, .eu, .in). Defaulting to .com but allowing override?
ACCOUNTS_URL_MAP = {
    "com": "https://accounts.zoho.com",
    "eu": "https://accounts.zoho.eu",
    "in": "https://accounts.zoho.in",
    "au": "https://accounts.zoho.com.au",
    "jp": "https://accounts.zoho.jp"
}

def get_refresh_token(client_id, client_secret, code, dc="com", redirect_uri="http://localhost:8000/callback"):
    """
    Exchanges the grant code for a refresh token.
    Step 2 of OAuth flow.
    """
    base_url = ACCOUNTS_URL_MAP.get(dc, ACCOUNTS_URL_MAP["com"])
    url = f"{base_url}/oauth/v2/token"
    
    # For Self Client, redirect_uri might need to be created as None or passed strictly if configured.
    # Often for Self Client, sending it might cause issues if not configured, or be ignored.
    # We'll include it if user didn't explicitly say not to, but usually it's safe to include if registered.
    # However, for pure 'Self Client' console generation, sometimes 'http://localhost' or similar is implicitly used or not needed.
    
    params = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if "error" in data:
            print(f"Error from Zoho: {data.get('error')}")
            return None

        return data
        
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        if 'response' in locals() and response:
             print(f"Response content: {response.text}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exchange Zoho Grant Code for Refresh Token")
    parser.add_argument("--client_id", required=True, help="Zoho Client ID")
    parser.add_argument("--client_secret", required=True, help="Zoho Client Secret")
    parser.add_argument("--code", required=True, help="Zoho Grant Code (Self Client)")
    parser.add_argument("--redirect_uri", default="http://localhost:8000/callback", help="Redirect URI (must match Client config)")
    parser.add_argument("--dc", default="com", choices=["com", "eu", "in", "au", "jp"], help="Zoho Data Center (e.g. com, eu, in)")
    
    args = parser.parse_args()
    
    print("--- Zoho Token Exchanger ---")
    result = get_refresh_token(args.client_id, args.client_secret, args.code, args.dc, args.redirect_uri)
    
    if result:
        print("\nSUCCESS! Here are your tokens:\n")
        print(f"Access Token: {result.get('access_token')}")
        print(f"Refresh Token: {result.get('refresh_token')}")
        print(f"Expires In: {result.get('expires_in')}")
        
        if result.get('refresh_token'):
            print("\nIMPORTANT: Save the 'Refresh Token' in your .env file as ZOHO_REFRESH_TOKEN.")
        else:
            print("\nWARNING: No Refresh Token received. Did you already use this code? Or is the scope 'offline_access' missing?")
            print("Note: For Self Client, scopes are usually prompt-based. Ensure you requested 'ZohoBooks.fullAccess.all'.")
    else:
        print("\nFailed to retrieve tokens.")
