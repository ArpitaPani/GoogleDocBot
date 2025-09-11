# auth.py
import os
import json
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# Add the scopes your app needs; include userinfo/email if you want to identify the user
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]

def _client_config():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    if not client_id or not client_secret or not redirect_uri:
        raise RuntimeError("Missing GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REDIRECT_URI env vars")
    return {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri]
        }
    }

def _make_flow():
    cfg = _client_config()
    flow = Flow.from_client_config(cfg, scopes=SCOPES)
    flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return flow

def start_auth_link():
    """
    Returns the URL to send the user to for Google sign-in.
    Save the state in session_state.
    """
    flow = _make_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",        # request refresh token
        include_granted_scopes="true",
        prompt="consent"             # force consent to ensure refresh_token is returned
    )
    st.session_state["oauth_state"] = state
    return auth_url

def exchange_code_for_credentials():
    """
    Call this when the redirect returns with ?code=...
    Exchanges the code for credentials, stores in session_state, returns Credentials or None.
    """
    query_params = st.experimental_get_query_params()
    if "code" not in query_params:
        return None

    code = query_params["code"][0]
    # Build a fresh flow and fetch the token using the code
    flow = _make_flow()
    # This will exchange the code for tokens (access + refresh)
    flow.fetch_token(code=code)
    creds = flow.credentials

    # Save minimal credential info in session for later restoration
    st.session_state["google_creds"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }

    # remove query params from URL so code doesn't stay visible
    st.experimental_set_query_params()
    return creds

def credentials_from_session():
    """
    Recreate google.oauth2.credentials.Credentials from session_state (if present)
    """
    data = st.session_state.get("google_creds")
    if not data:
        return None
    return Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes")
    )
