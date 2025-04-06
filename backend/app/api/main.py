from fastapi import FastAPI, APIRouter
from app.mcp_tools import mcp as mcp_server
from app.models import ChatRequest
from app.mcp_client import MCPClient
from fastapi.middleware.cors import CORSMiddleware
import os

mcp_client = MCPClient(os.getenv("MCP_BUILDING_SENSORS_URL"))


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/")
def root():
    return {"result": "success"}


@router.post("/responses")
async def responses(chat_request: ChatRequest):
    response = await mcp_client.process_query(chat_request.message)
    return {"result": response}


app.include_router(router)
app.mount("/", app=mcp_server.sse_app())
