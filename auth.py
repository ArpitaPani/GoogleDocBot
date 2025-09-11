import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import streamlit as st

# OAuth Scopes
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]
CREDENTIALS_PATH = "credentials.json"
REDIRECT_URI = "http://localhost:8501/"


def get_oauth_login_url():
    """Generate Google OAuth login URL."""
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError("Missing credentials.json in project root.")

    flow = Flow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    auth_url, state = flow.authorization_url(prompt="consent", access_type="offline")
    return auth_url, state


def exchange_code_for_credentials(auth_code):
    """Exchange auth code for credentials."""
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_PATH, scopes=SCOPES, redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(code=auth_code)
    return flow.credentials


def get_google_creds():
    """Handle OAuth in Streamlit."""
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        creds = exchange_code_for_credentials(code)
        return creds
    return None
