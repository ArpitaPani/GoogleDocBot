import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import streamlit as st

# Google API scopes
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]

# Local credentials file path
CREDENTIALS_PATH = "credentials.json"

# 🔑 Update to your deployed app URL
REDIRECT_URI = "https://googledocbot.onrender.com/"


def ensure_credentials_file():
    """Ensure credentials.json exists by writing from env var if needed."""
    if not os.path.exists(CREDENTIALS_PATH):
        creds_json = os.getenv("GOOGLE_OAUTH_JSON")
        if not creds_json:
            raise FileNotFoundError(
                "❌ Missing credentials.json file and GOOGLE_OAUTH_JSON env var."
            )
        with open(CREDENTIALS_PATH, "w") as f:
            f.write(creds_json)


def get_oauth_login_url():
    """Generate Google OAuth login URL."""
    ensure_credentials_file()
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    auth_url, state = flow.authorization_url(
        prompt="consent", access_type="offline", include_granted_scopes="true"
    )
    return auth_url, state


def exchange_code_for_credentials(auth_code):
    """Exchange auth code for credentials."""
    ensure_credentials_file()
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    flow.fetch_token(code=auth_code)
    return flow.credentials


def get_google_creds():
    """Retrieve Google credentials if OAuth code is present in query params."""
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        creds = exchange_code_for_credentials(code)
        return creds
    return None
