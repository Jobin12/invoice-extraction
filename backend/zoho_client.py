import requests
import os
import json
from datetime import datetime

class ZohoClient:
    def __init__(self):
        self.client_id = os.getenv("ZOHO_CLIENT_ID")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET")
        self.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
        self.org_id = os.getenv("ZOHO_ORG_ID")
        self.dc = os.getenv("ZOHO_DC", "com")
        
        # DC Maps
        self.accounts_url_map = {
            "com": "https://accounts.zoho.com",
            "eu": "https://accounts.zoho.eu",
            "in": "https://accounts.zoho.in",
            "au": "https://accounts.zoho.com.au",
            "jp": "https://accounts.zoho.jp"
        }
        
        self.api_url_map = {
            "com": "https://www.zohoapis.com",
            "eu": "https://www.zohoapis.eu",
            "in": "https://www.zohoapis.in",
            "au": "https://www.zohoapis.com.au",
            "jp": "https://www.zohoapis.jp"
        }

        self.base_url = f"{self.api_url_map.get(self.dc, self.api_url_map['com'])}/books/v3"
        self.access_token = None
        
        if not all([self.client_id, self.client_secret, self.refresh_token, self.org_id]):
            print("Warning: Zoho credentials not fully configured in environment.")

        print(f"ZohoClient Initialized. DC: {self.dc}, Org: {self.org_id}")
        
    def _get_access_token(self):
        """
        Refreshes the access token using the refresh token.
        Example response: {"access_token": "...", "api_domain": "...", "token_type": "Bearer", "expires_in": 3600}
        """
        accounts_url = self.accounts_url_map.get(self.dc, self.accounts_url_map["com"])
        url = f"{accounts_url}/oauth/v2/token"
        params = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                raise Exception(f"Zoho Auth Error: {data.get('error')}")
                
            self.access_token = data.get("access_token")
            return self.access_token
            
        except Exception as e:
            print(f"Failed to refresh token: {e}")
            raise

    def _get_headers(self):
        if not self.access_token:
            self._get_access_token()
        return {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json"
        }

    def search_customer(self, customer_name):
        """
        Searches for a customer by name.
        Returns the first match's contact_id.
        """
        url = f"{self.base_url}/contacts"
        params = {
            "organization_id": self.org_id,
            "contact_name": customer_name
        }
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        
        if response.status_code == 401:
            # Token might be expired, retry once
            self._get_access_token()
            response = requests.get(url, headers=self._get_headers(), params=params)
            
        if response.status_code != 200:
            print(f"Error searching customer: {response.text}")
            return None
            
        data = response.json()
        contacts = data.get("contacts", [])
        
        if contacts:
            return contacts[0].get("contact_id")
        return None

    def create_invoice(self, invoice_data, customer_id):
        """
        Creates an invoice in Zoho Books.
        """
        url = f"{self.base_url}/invoices"
        params = {"organization_id": self.org_id}
        
        # Format date format YYYY-MM-DD
        date_str = self._format_date_for_zoho(invoice_data.get("invoice_date"))
        
        line_items = []
        for item in invoice_data.get("line_items", []):
            line_items.append({
                "description": item.get("description"),
                "rate": self._parse_float(item.get("unit_price")),
                "quantity": self._parse_float(item.get("quantity"))
            })

        payload = {
            "customer_id": customer_id,
            "date": date_str,
            "reference_number": invoice_data.get("invoice_number"), # Use extracted number as reference
            # "invoice_number": invoice_data.get("invoice_number"), # Omitted to let Zoho auto-generate
            "line_items": line_items,
            # "due_date": invoice_data.get("due_date"), # Optional
        }
        
        print(f"Creating invoice with payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, headers=self._get_headers(), params=params, json=payload)
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Failed to create invoice. Status: {response.status_code}. Response: {response.text}")
            # Identify error message
            try:
                err = response.json()
                return {"error": err.get("message", "Unknown error")}
            except:
                return {"error": response.text}

    def _format_date_for_zoho(self, date_str):
        """
        Parses various date formats and converts to YYYY-MM-DD for Zoho.
        """
        if not date_str:
            return datetime.today().strftime('%Y-%m-%d')
            
        # List of supported formats
        formats = [
            "%b %d, %Y",       # Aug 14, 2025
            "%B %d, %Y",       # August 14, 2025
            "%d %b %Y",        # 14 Aug 2025
            "%d %B %Y",        # 14 August 2025
            "%Y-%m-%d",        # 2025-08-14
            "%d-%m-%Y",        # 14-08-2025
            "%d/%m/%Y",        # 14/08/2025
            "%m/%d/%Y",        # 08/14/2025
            "%Y/%m/%d"         # 2025/08/14
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        print(f"Warning: Could not parse date '{date_str}'. Sending original.")
        return date_str

    def _parse_float(self, value):
        if not value: return 0.0
        if isinstance(value, (int, float)): return float(value)
        try:
            # Clean string "1,200.00" -> 1200.00
            clean = str(value).replace(",", "").replace("$", "").strip()
            return float(clean)
        except:
            return 0.0
