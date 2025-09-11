import os
import json
from google.oauth2 import service_account

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]

def authenticate():
    """
    Authenticate with Google Service Account credentials from environment variable.
    """
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if not creds_json:
        raise ValueError("Missing GOOGLE_CREDENTIALS environment variable")

    creds_dict = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES
    )

    print("✅ Authentication successful (Service Account).")
    return creds


if __name__ == "__main__":
    authenticate()
