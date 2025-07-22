# utils/auth.py
"""
OAuth2 helper that automatically upgrades the stored token whenever
new scopes are requested.

• Stores client‑ID in   credentials.json   (downloaded from Google Cloud).
• Stores user token in   token.json        (created on first run).

Usage:
    from utils.auth import get_creds
    creds = get_creds([
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/spreadsheets",
    ])
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# --------------------------------------------------------------------------- #
# File locations – change if you like
# --------------------------------------------------------------------------- #
CREDS_FILE = Path("credentials.json")  # OAuth client secrets from GCP console
TOKEN_FILE = Path("token.json")        # Cached user token


# --------------------------------------------------------------------------- #
# Public helper
# --------------------------------------------------------------------------- #
def get_creds(scopes: Sequence[str]) -> Credentials:
    """
    Return valid Credentials that satisfy *all* requested scopes.
    • If token.json is missing, or doesn’t cover all scopes, the browser
      consent flow is triggered automatically.
    • The refreshed / upgraded token is saved back to token.json.

    Parameters
    ----------
    scopes : list[str]
        All OAuth scopes the caller needs.

    Returns
    -------
    google.oauth2.credentials.Credentials
    """
    if not CREDS_FILE.exists():
        raise FileNotFoundError(
            f"Google client‑secret file not found: {CREDS_FILE.resolve()}"
        )

    creds: Credentials | None = None

    # 1) Load existing token -------------------------------------------------
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, scopes=[])

    # 2) Check validity & required scopes -----------------------------------
    needs_flow = (
        creds is None
        or not creds.valid
        or not creds.has_scopes(scopes)
    )

    if needs_flow:
        # Interactive browser flow – merges any previously granted scopes
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDS_FILE, scopes=scopes
        )
        creds = flow.run_local_server(port=0, prompt="consent")
        _save_token(creds)

    elif creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_token(creds)

    return creds


def _save_token(creds: Credentials):
    """Write the current credentials to TOKEN_FILE."""
    TOKEN_FILE.write_text(creds.to_json())
    print(f"[AUTH] Token stored/updated with scopes: {', '.join(creds.scopes)}")
