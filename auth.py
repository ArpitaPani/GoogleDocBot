import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import os, json
from google.oauth2 import service_account

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = service_account.Credentials.from_service_account_info(creds_dict)

# OAuth Scopes for Google Drive and Docs
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/documents.readonly'
]

TOKEN_PATH = 'token.json'
CREDENTIALS_PATH = 'credentials.json'


def authenticate():
    """
    Authenticate with Google OAuth 2.0, create token.json.
    This will open a browser window for login.
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    "Missing credentials.json. Please download from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save for next run
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    print("✅ Authentication successful. Token saved to token.json.")
    return creds


if __name__ == "__main__":
    authenticate()
