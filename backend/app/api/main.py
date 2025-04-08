from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import agents
from app.models import ChatRequest

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def root():
    return {"result": "success"}


@app.post("/responses")
async def responses(chat_request: ChatRequest):
    response = await agents.run(chat_request.message)
    return {"result": response}
