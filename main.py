"""Single FastAPI cloud service; optional mounted MCP streamable HTTP adapter."""
import hmac
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from decisioniq.agent import demo_chat, frontier_chat
from decisioniq.tools import SCHEMAS, DESCRIPTIONS, execute

BASE=Path(__file__).resolve().parent
mcp_server=None
mcp_app=None
if os.getenv('ENABLE_MCP','0')=='1':
    from decisioniq.mcp_integration import build_mcp_app
    mcp_server,mcp_app=build_mcp_app()

@asynccontextmanager
async def lifespan(app:FastAPI):
    if mcp_server:
        async with mcp_server.session_manager.run():
            yield
    else:
        yield

app=FastAPI(title='DecisionIQ Copilot',version='0.1.0',
            description='Synthetic business-card decision analytics with optional frontier-model reasoning.',
            lifespan=lifespan)

class ChatInput(BaseModel):
    message:str=Field(min_length=3,max_length=1200)
    history:list[dict]=Field(default_factory=list,max_length=6)

class RunTool(BaseModel):
    arguments:dict=Field(default_factory=dict)

@app.get('/health')
def health():
    return {'status':'ok','mode':'frontier_available' if os.getenv('ENABLE_LLM')=='1' and os.getenv('OPENAI_API_KEY') else 'offline_demo',
            'mcp_enabled':bool(mcp_server),'dataset':'synthetic_only'}

@app.get('/api/catalog')
def catalog():
    return {'tools':[{'name':n,'description':DESCRIPTIONS[n], 'schema':schema.model_json_schema()}
                      for n,schema in SCHEMAS.items()],
            'synthetic':True,'frontier_enabled':os.getenv('ENABLE_LLM')=='1' and bool(os.getenv('OPENAI_API_KEY'))}

@app.post('/api/tools/{tool_name}')
def tool_run(tool_name:str,payload:RunTool):
    try:
        return execute(tool_name,payload.arguments)
    except Exception as err:
        raise HTTPException(status_code=422, detail=f'Tool rejected input: {type(err).__name__}')

@app.post('/api/chat')
def chat(body:ChatInput, x_access_token:str|None=Header(default=None)):
    if os.getenv('ENABLE_LLM')!='1':
        return demo_chat(body.message)
    # Paid API calls must not be anonymously accessible. Use strong token and edge-level rate limiting in deployment.
    expected=os.getenv('COPILOT_ACCESS_TOKEN','')
    if len(expected)<20:
        raise HTTPException(status_code=503,detail='Live AI requires a long COPILOT_ACCESS_TOKEN; configure the service')
    if not x_access_token or not hmac.compare_digest(x_access_token,expected):
        raise HTTPException(status_code=401, detail='Live AI requires a valid private access token')
    if not os.getenv('OPENAI_API_KEY'):
        raise HTTPException(status_code=503,detail='Frontier API is not configured')
    try:
        return frontier_chat(body.message,body.history)
    except Exception as exc:
        # Do not leak API credentials, request content or provider error details to end users.
        raise HTTPException(status_code=502,detail=f'Frontier request could not complete ({type(exc).__name__}); check server logs')

app.mount('/assets',StaticFiles(directory=BASE/'web'),name='assets')

@app.get('/')
def index():
    return FileResponse(BASE/'web'/'index.html')

# Catch-all MCP mount MUST be registered last to preserve routes above.
if mcp_app:
    app.mount('/',mcp_app,name='mcp')
