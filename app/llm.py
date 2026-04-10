# async azure openai call
import httpx
from app.config import settings

async def call_azure_openai(messages):
    url = f"{settings.AZURE_OPENAI_ENDPOINT}/openai/deployments/{settings.AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version={settings.AZURE_OPENAI_API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": settings.AZURE_OPENAI_API_KEY
    }
    payload = {
        "messages": messages,
        "max_tokens": 500,
        "temperature": 0.7,
        "model": settings.AZURE_OPENAI_DEPLOYMENT_NAME 
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
# httpx.AsyncClient is the async equivalent of requests. 
# The async with block ensures the HTTP connection is properly closed after use — no connection leaks.
#  timeout=30.0 means if Azure doesn't respond in 30 seconds, 
#  it raises a TimeoutException instead of hanging forever.

# Request = URL + Headers + Body. Think of it like sending a courier package. The URL is the delivery address, the headers are the customs form (who sent it, what's inside), and the body/payload is the actual package contents.
# httpx is your postman. You don't speak raw TCP/HTTP yourself — you hand httpx.AsyncClient a Python dict and it converts it into a proper HTTP packet and sends it. requests does the same thing but is synchronous (blocking). httpx is async — it can send many requests concurrently without waiting for each one to finish.
# Why async with? Opening an HTTP client creates a connection pool under the hood. async with guarantees that pool is cleanly shut down after the call, even if an exception is thrown — no dangling connections.
# Headers specifically serve two purposes here. api-key is authentication — Azure reads this first and rejects the request immediately if it's missing or wrong, before even touching your messages. Content-Type: application/json tells Azure how to parse the body — without it, Azure would receive raw bytes and not know they're JSON.
# raise_for_status() is your safety net. If Azure returns a 401 Unauthorized (bad api-key) or 429 Too Many Requests (rate limit hit), this line converts that silent HTTP error code into a loud Python exception that your error handler can catch.
# Click any box in the diagram to go deeper on that concept