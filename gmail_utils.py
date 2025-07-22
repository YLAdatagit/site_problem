# gmail_utils.py
"""
Helpers for talking to Gmail:
• search for threads that match an arbitrary query
• download the newest .xlsx / .xlsm attachment from the newest matching thread
• mark thread as read so it won’t be processed again
"""

from __future__ import annotations

import base64
import os
import re
import tempfile
from pathlib import Path
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.auth import get_creds
from utils.log import log


# --------------------------------------------------------------------------- #
# Constants / scopes
# --------------------------------------------------------------------------- #
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/spreadsheets",   # add this line
]

ATTACHMENT_EXTS = (".xlsx", ".xlsm")  # add more if needed


# --------------------------------------------------------------------------- #
# Public helper
# --------------------------------------------------------------------------- #
def get_latest_attachment(tmp_dir: str | Path) -> Optional[Path]:
    """
    Search Gmail using GMAIL_QUERY (.env), find the newest thread,
    download the first Excel attachment found (xlsx/xlsm) in the thread
    (starting from newest message), save it in tmp_dir, mark thread read,
    and return the file path.  Returns None when nothing is found.
    """
    query = os.getenv("GMAIL_QUERY", "").strip()
    if not query:
        log.error("Environment variable GMAIL_QUERY is empty.")
        return None

    log.info(f"Using Gmail query: {query}")

    # Build Gmail service
    creds = get_creds(SCOPES)
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    try:
        # ------------------------------------------------------------------- #
        # 1. Search for matching threads (returns newest first by default)
        # ------------------------------------------------------------------- #
        response = service.users().threads().list(
            userId="me", q=query, maxResults=10
        ).execute()
        threads = response.get("threads", [])

        if not threads:
            log.warning("Gmail query returned 0 threads.")
            return None

        # ------------------------------------------------------------------- #
        # 2. Pick the newest thread
        # ------------------------------------------------------------------- #
        latest_thread_id = threads[0]["id"]
        log.info(f"Newest thread ID: {latest_thread_id}")

        thread = (
            service.users()
            .threads()
            .get(userId="me", id=latest_thread_id, format="full")
            .execute()
        )

        # ------------------------------------------------------------------- #
        # 3. Look through messages newest → oldest
        # ------------------------------------------------------------------- #
        messages = thread.get("messages", [])[::-1]  # reverse list → newest first
        for msg in messages:
            msg_id = msg["id"]
            parts = msg["payload"].get("parts", [])
            # Some messages have a single body part; wrap it
            if msg["payload"].get("filename"):
                parts.append(msg["payload"])

            filenames = [p.get("filename", "") for p in parts]
            log.info(f"Message {msg_id} attachments: {', '.join(filenames) or '—'}")

            for part in parts:
                filename = part.get("filename", "")
                if filename.lower().endswith(ATTACHMENT_EXTS):
                    # -- Found a viable attachment --
                    attach_id = part["body"]["attachmentId"]
                    data = (
                        service.users()
                        .messages()
                        .attachments()
                        .get(userId="me", messageId=msg_id, id=attach_id)
                        .execute()["data"]
                    )
                    binary = base64.urlsafe_b64decode(data)

                    # Clean filename to be filesystem‑safe
                    safe_name = re.sub(r"[^\w.\-]", "_", filename)
                    out_path = Path(tmp_dir) / safe_name
                    with open(out_path, "wb") as fh:
                        fh.write(binary)

                    log.success(f"Downloaded attachment → {out_path}")

                    # Mark the whole thread as read
                    service.users().threads().modify(
                        userId="me",
                        id=latest_thread_id,
                        body={"removeLabelIds": ["UNREAD"]},
                    ).execute()

                    return out_path

        # ------------------------------------------------------------------- #
        # 4. No Excel attachment found in any message
        # ------------------------------------------------------------------- #
        log.warning(
            "Thread contained no .xlsx/.xlsm attachment in any message. Skipping."
        )
        # Still mark as read so we don’t look at it again tomorrow
        service.users().threads().modify(
            userId="me", id=latest_thread_id, body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        return None

    except HttpError as err:
        log.error(f"Gmail API error: {err}")
        return None
