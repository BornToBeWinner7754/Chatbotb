from fastapi import FastAPI, HTTPException
from app.schemas import ChatRequest, ChatResponse #pydantic model define the shape of request response data/json
from app.session_manger import session_manager  #the shared in memeory store we created earlier to manage conversation history
from app.llm import call_azure_openai   #the async httpx function that calls Azure OpenAI
from app.agent import run_agent  #the agent logic that decides when to call tools
import asyncio
# creates the fast api application instance
app = FastAPI(title="Async Chatbot API")
@app.post("/chat",response_model=ChatResponse)
# @app.post("/chat") registers this function to handle the POST /chat endpoint. When a client sends a POST request to /chat, this function will be called.
# response model= Chatresponse tells the fastapi to automatically convert the return value of this function into a ChatResponse object and then serialize it to JSON for the HTTP response.
async def chat(request:ChatRequest):
    # Fastapi parses the incoming json body of the request and converts it into Chatrequest object, which is then passed as the argument to this function. So request.message and request.session_id are available for us to use.
    # if json is missing fields or has wrong types fastapi returns 422 Unprocessable Entity error before even calling this function.

    # step 1 fetch this sessions converstation history from the session manager
    history = await session_manager.get_history(request.session_id)
    #sessionid identifies the user/session, and get_history returns the list of messages for that session. 
    # If this is a new session_id, it will return an empty list.
    # get_history acquires the asyncio lock to ensure thread safety when accessing the shared sessions store.
    # concurrent requests. Returns a list like: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    # If this is a brand new session_id, defaultdict returns [] automatically.


    #  Step 2 Persist the incoming user message to the session store
    # we add the new user message to the history before calling Azure so that the full conversation context is sent to Azure.
    await session_manager.add_message(request.session_id,role="user",content=request.message)

    # step 3 : build the full message list to send to azure openai
    messages = history + [{"role":"user","content":request.message}]
    # the openai chat format requires the full conversation history every time 
    # the model has no memory of previous call
    # We append the new user message on top of the existing history.
    # Result looks like:
    #   [
    #     {"role": "user",      "content": "Hi"},
    #     {"role": "assistant", "content": "Hello!"},
    #     {"role": "user",      "content": "What is Python?"}   ← new message



    #step 3 call azure openai non blocking async http call
    # await yields control back to the event loop while waiting for the Azure OpenAI response, allowing other requests to be processed concurrently.
    # for Azure's response. Other requests can be handled during this wait.
    # This is the key advantage over sync code — no thread is blocked.
    try:
        response_text = await call_azure_openai(messages)

        # persist the assistant reply to the session history so that it's included in future calls to Azure for context.
        await session_manager.add_message(request.session_id,"assistant",response_text)

        #fastapi serializes this ChatResponse object to JSON and sends it back to the client as the HTTP response body.
         # Response body: {"session_id": "abc", "response": "..."}
        return ChatResponse(session_id=request.session_id,response=response_text)
    except Exception as e:
        # If any error occurs (e.g., Azure returns an error, network issue), we catch it and return a 500 Internal Server Error with the error message.
        raise HTTPException(status_code=500,detail=str(e))
