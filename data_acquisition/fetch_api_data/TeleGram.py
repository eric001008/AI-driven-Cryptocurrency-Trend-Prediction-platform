#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch recent messages from public Telegram channels, filter by keywords,
and write to PostgreSQL.

"""

import os
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime
# Ensure telegram_session/ directory exists relative to project root
session_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../telegram_session"))
os.makedirs(session_dir, exist_ok=True)

SEARCH_KEYWORDS = [
    "cryptocurrency", "bitcoin", "ethereum", "crypto ban",
    "rate hike", "bank collapse", "liquidity crisis"
]

# Load configuration from environment
API_ID     = int(os.getenv("TELEGRAM_API_ID",  "0"))
API_HASH   = os.getenv("TELEGRAM_API_HASH", "")
SESSION = os.path.join(session_dir, "teleparser_session")
CHANNELS   = os.getenv("TELEGRAM_CHANNELS", "").split(",")
LIMIT      = int(os.getenv("TELEGRAM_LIMIT", "0"))

# Initialize Telethon client
client = TelegramClient(SESSION, API_ID, API_HASH)
# Use user login (phone + code), not bot_token
client.connect()
if not client.is_user_authorized():
    raise Exception("Telegram session not authorized. Please login locally and mount the .session file.")


def fetch_and_transform(channel: str, limit: int = 0) -> list:
    """
    Fetches messages from a single public Telegram channel,
    filters by SEARCH_KEYWORDS, and returns a list of dicts:
    """
    # Resolve channel entity (accept with or without '@')
    channel_id = channel.lstrip("@")
    entity = client.get_entity(channel_id)

    offset_id = 0
    step = 100
    all_messages = []

    while True:
        history = client(GetHistoryRequest(
            peer=entity,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=step,
            max_id=0,
            min_id=0,
            hash=0
        ))
        msgs = history.messages
        if not msgs:
            break

        for m in msgs:
            text = m.message or ""
            # Keep only messages containing any of the keywords
            if any(kw.lower() in text.lower() for kw in SEARCH_KEYWORDS):
                all_messages.append({
                    "id":        m.id,
                    "date":      m.date.isoformat(),
                    "sender_id": getattr(m.sender, 'id', None),
                    "text":      text,
                    "views":     getattr(m, 'views', None),
                    "forwards":  getattr(m, 'forwards', None)
                })

        offset_id = msgs[-1].id
        # If a limit is set and it is reached or exceeded, stop
        if limit and len(all_messages) >= limit:
            break

    return all_messages


def fetch_teleparser(cur):
    """
    Fetches filtered messages for all configured channels and inserts
    into ods.telegram_messages table.
    """
    print("\n##### Acquisition: Telegram #####\n")
    for channel in CHANNELS:
        msgs = fetch_and_transform(channel, LIMIT)
        for msg in msgs:
            cur.execute("""
                INSERT INTO ods.telegram_messages (
                    channel, message_id, sent_at,
                    sender_id, content, views, forwards
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (message_id) DO NOTHING;
            """, (
                channel.lstrip("@"),
                msg["id"],
                msg["date"],
                msg["sender_id"],
                msg["text"],
                msg["views"],
                msg["forwards"]
            ))
    # Commit transaction
    cur.connection.commit()

# Ensure clean disconnect on exit
def _shutdown():
    client.disconnect()

import atexit
atexit.register(_shutdown)
