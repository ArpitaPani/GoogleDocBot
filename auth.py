import os
import json
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import streamlit as st

# OAuth scopes for Google Drive + Docs
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]

def authenticate():
    """
    Authenticate user with Google OAuth.
    """
    if "google_creds" in st.session_state:
        return st.session_state["google_creds"]

    creds = None
    client_json = os.environ.get("GOOGLE_OAUTH_CLIENT")
    if not client_json:
        st.error("❌ Missing GOOGLE_OAUTH_CLIENT environment variable in Render.")
        return None

    client_config = json.loads(client_json)

    # If no credentials is in session then the OAuth flow can be started
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = st.secrets.get("REDIRECT_URI", "http://localhost:8501/oauth2callback")

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    st.write(f"[Login with Google]({auth_url})")


    if creds:
        st.session_state["google_creds"] = creds
        return creds

    return None
