import os

class Settings:
    def __init__(self):
        # Zoho region (e.g., 'com', 'eu', 'in')
        self.ZOHO_REGION = os.getenv('ZOHO_REGION', 'com')
        # Domain used by zoho_service to build URLs (e.g., zoho.com)
        self.ZOHO_DOMAIN = f"zoho.{self.ZOHO_REGION}"
        self.ZOHO_CLIENT_ID = os.getenv('ZOHO_CLIENT_ID', '')
        self.ZOHO_CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET', '')
        self.ZOHO_REDIRECT_URI = os.getenv('ZOHO_REDIRECT_URI', '')
        # Optional cached token for debugging (normally fetched via OAuth flow)
        self.ZOHO_ACCESS_TOKEN = os.getenv('ZOHO_ACCESS_TOKEN', '')

# Export a singleton used throughout the codebase
settings = Settings()
