# Deployment plan: public demo → private LLM → MCP testing → plugin submission

## Phase A — public free demonstration

1. Create a cloud project; enable Cloud Run, Cloud Build and Artifact Registry; configure billing and IAM.
2. Build the Docker image locally if Docker is available, or deploy direct from the source folder with `gcloud run deploy decisioniq-copilot --source . --region us-central1 --allow-unauthenticated --set-env-vars ENABLE_LLM=0,ENABLE_MCP=0`.
3. Verify `/health`, `/api/catalog`, all five tools, and browser UI. The server starts on `PORT` and can scale to zero on Cloud Run.
4. Set Cloud Run max instances, service quotas and error monitoring appropriate to budget. There is no LLM API expense in offline mode, but cloud usage can still incur costs.
5. Add your own domain if you need a brand-stable URL; Cloud Run's service URL itself is stable while the service remains provisioned.

## Phase B — opt-in frontier model

1. Keep `OPENAI_API_KEY` in a cloud secret manager; never put it in Git, in JavaScript, or the image.
2. Make `COPILOT_ACCESS_TOKEN` a separate random 32+ byte secret; use Cloud Run secret mappings and `ENABLE_LLM=1`.
3. Confirm the configured `OPENAI_MODEL` is accessible to your API account and supports the Responses API function tool flow.
4. Add user login or OAuth, request throttling/quotas, per-user bill caps, audit logging without sensitive content, and incident-response controls before general access. The demo token is not a complete authentication solution.
5. Avoid logging raw conversation content; limit request body sizes at edge and monitor failures.

## Phase C — remote MCP adapter (requires SDK v2)

MCP can serve the **same five tools** independently of the OpenAI API. A ChatGPT host already supplies the language model. It need not call your Responses API.

1. Install `mcp>=2,<3` (bundled in production requirements).
2. Get your deployed hostname (no scheme), e.g. `decisioniq-abc.a.run.app`.
3. Set `ENABLE_MCP=1` and `MCP_ALLOWED_HOSTS` to that exact host; optionally configure precise `MCP_ALLOWED_ORIGINS` for browser MCP clients. No wildcard hosts. Do not turn on an unverified server.
4. Restart the service. It mounts Streamable HTTP under `/mcp` and starts the SDK session manager at the application lifespan.
5. Verify the protocol with the official MCP client/Inspector. Example:

```python
import asyncio
from mcp import Client

async def check():
    async with Client('https://YOUR_DEPLOYED_HOST/mcp') as client:
        tools = await client.list_tools()
        print([t.name for t in tools.tools])

asyncio.run(check())
```

6. Confirm that each tool responds to valid inputs, rejects invalid values, enforces read-only operation, and exposes no secrets. Because only a published synthetic dataset is used, a public read-only MCP may be adequate for development; **do not add private data without OAuth, authorization checks and consent controls**.
7. Cloud Run cold starts and statelessness can affect long-lived MCP sessions; assess SDK's stateless HTTP mode, routing, scale-to-zero behavior, and multi-instance sessions under load before treating the integration as production ready.

## Phase D — ChatGPT plugin submission

1. Generate a manifest ZIP using `scripts/prepare_plugin.py` after the remote HTTPS MCP endpoint is live.
2. Provide genuine publisher/domain identity, homepage, support and privacy URLs, suitable assets, 5 positive and 3 negative review cases, test credentials (if needed), and a video demonstration.
3. Register the MCP connection in ChatGPT's current developer/plugin flow. Complete domain verification and MCP tool scan.
4. Run tests in the target host, fix findings, submit for review. **No public installation is available until the listing is approved and explicitly published.**

Reference docs:
- https://developers.openai.com/plugins/build/mcp-server
- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins/deploy/connect-chatgpt
- https://developers.openai.com/plugins/deploy/submission
- https://py.sdk.modelcontextprotocol.io/run/asgi/
- https://docs.cloud.google.com/run/docs/deploying-source-code
