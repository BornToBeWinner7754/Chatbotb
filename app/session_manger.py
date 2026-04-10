# uses lock + in memory store(thread safe +async)
import asyncio
from collections import defaultdict

# SessionManager handles per-user/per-session conversation history
# in a thread-safe way for async environments (e.g., FastAPI)
class SessionManager:
    def __init__(self):
        # defaultdict(list) means: if a session_id doesn't exist yet,
        # automatically create an empty list for it on first access.
        # Structure: { "session_abc": [ {role, content}, ... ], ... }
        self.sessions = defaultdict(list)
        # asyncio.Lock ensures only one coroutine can read/write
        # sessions at a time — prevents race conditions when multiple
        # users hit the API simultaneously
        self.lock = asyncio.Lock()

    async def get_history(self,session_id: str):
        # Acquire the lock before reading — no other coroutine can
        # touch self.sessions until we exit this block
        async with self.lock:
            # Returns the message list for this session.
            # If session_id is new, defaultdict returns [] automatically
            return self.sessions[session_id]
        
    async def add_message(self,session_id:str,role:str,content:str):
        # Acquire the lock before modifying sessions
        async with self.lock:
            # Append the new message to the session's history
            self.sessions[session_id].append({"role": role, "content": content})

session_manager = SessionManager()