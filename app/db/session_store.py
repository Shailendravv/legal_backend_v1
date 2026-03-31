from typing import List, Optional
from datetime import datetime
from supabase import create_client, Client
from pydantic import BaseModel
from app.core.config import settings
from app.core.logger import logger

class Turn(BaseModel):
    role: str
    content: str
    timestamp: datetime

class SessionStore:
    def __init__(self):
        self.url: str = settings.SUPABASE_URL
        self.key: str = settings.SUPABASE_KEY
        self.supabase: Client = create_client(self.url, self.key)
        logger.info("Supabase client initialized successfully.")

    def get_history(self, session_id: str, last_n: int = 10) -> List[Turn]:
        """
        Retrieves the last n turns of a session's history from Supabase.
        """
        try:
            response = self.supabase.table("sessions") \
                .select("role, content, created_at") \
                .eq("session_id", session_id) \
                .order("created_at", desc=True) \
                .limit(last_n) \
                .execute()
            
            # Since we fetched in descending order, we reverse it to preserve chronological order
            history = [
                Turn(role=row['role'], content=row['content'], timestamp=datetime.fromisoformat(row['created_at']))
                for row in reversed(response.data)
            ]
            return history
        except Exception as e:
            logger.error(f"Error retrieving history for session {session_id}: {str(e)}")
            return []

    def save_turn(self, session_id: str, role: str, content: str):
        """
        Saves a single turn of conversation to Supabase.
        """
        try:
            self.supabase.table("sessions").insert({
                "session_id": session_id,
                "role": role,
                "content": content
            }).execute()
            logger.debug(f"Saved {role} turn to session {session_id}")
        except Exception as e:
            logger.error(f"Error saving turn for session {session_id}: {str(e)}")

    def delete_session(self, session_id: str):
        """
        Deletes all turns related to a specific session ID.
        """
        try:
            self.supabase.table("sessions").delete().eq("session_id", session_id).execute()
            logger.info(f"Deleted history for session {session_id}")
        except Exception as e:
            logger.error(f"Error deleting history for session {session_id}: {str(e)}")

session_store = SessionStore()
