# DecisionIQ — Free GitHub Pages Showcase + Full Python Copilot

> **Two clearly separated experiences:** the public GitHub Pages **CardGrowth strategy lab** is real, browser-executable static analytics. The complete DecisionIQ conversational copilot is **locally runnable Python/ FastAPI source**, with optional frontier-model API and MCP integration. **The GitHub Pages demo does NOT host the DecisionIQ Python/chat backend.** All datasets and business results are synthetic.

## Publish your zero-charge demo

1. Extract this ZIP. Its contents (not the enclosing ZIP) are the repository root.
2. Create a **public** GitHub repository named `decisioniq-copilot` using https://github.com/new. Do not add an initial README because one is already included.
3. Upload all extracted files and directories, maintaining the folder structure. Alternatively use Git CLI:

```bash
git init
git add .
git commit -m "Publish DecisionIQ portfolio and static CardGrowth lab"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/decisioniq-copilot.git
git push -u origin main
```

4. In GitHub open repository **Settings → Pages → Build and deployment**. Choose **Deploy from a branch**, **main**, **/docs**, then **Save**.
5. Open `https://YOUR_USERNAME.github.io/decisioniq-copilot/`. This displays the portfolio landing page. Click **Launch live strategy lab** to open `docs/lab/index.html`.
6. Verify budget/offer sliders and interactive calculations; verify that the source link returns to the GitHub repository. Replace `YOUR_USERNAME` in resume links; never commit `.env`, tokens or API keys.

### Live demo structure

- `docs/index.html` — *new* responsive landing page, with accurate separation between the hosted static lab and the local Python copilot.
- `docs/lab/index.html` — original CardGrowth AI static decision lab (prebuilt and interactive).
- `docs/lab/assets/data.json` — precomputed synthetic CardGrowth scenario data.
- `docs/preview.png` — screenshot of the actual, separately runnable DecisionIQ interface.

The `docs/` folder is a static public demo. FastAPI endpoints such as `/api/chat` will **not** work on GitHub Pages, because GitHub Pages does not run Python servers.

## Run the complete DecisionIQ copilot locally (free offline mode)

```bash
python -m pip install -r requirements-local.txt
python -m unittest discover -s tests -v
uvicorn main:app --reload --port 8080
```

Open `http://localhost:8080`. This is a separate application from the static portfolio pages. To optionally use frontier-model reasoning, follow the existing instructions below and use a private API key; model usage may incur charges.

---

# DecisionIQ Copilot — Business Strategy as a Tool-Grounded AI Product

**Status:** runnable local portfolio MVP. **Not hosted or publicly published.** Built as an independent continuation of CardGrowth AI Project 3, not a record of TCS / Globe / Capital One client deployment.

## 60-second overview

DecisionIQ makes business strategy analysis conversational while keeping numerical facts in **five deterministic, testable Python tools**. It is available in two modes:

- **Offline public-demo mode (default):** no OpenAI calls, no API key, uses deterministic question routing/templates; anybody who visits the hosted site can use it without paying or signing in. This is NOT frontier AI.
- **Private frontier mode (opt-in):** backend calls the OpenAI **Responses API** with function tools, returns auditable tool traces, and requires a long access token. It incurs API charges. No API key or token is stored in the browser's source code.

A second, **optional MCP adapter** exposes the same read-only tools through Streamable HTTP at `/mcp`, ready to test as a private ChatGPT plugin once the official Python MCP SDK is installed and the endpoint is deployed. MCP integration is untested in this offline build environment (SDK not available), so do not call it production validated.

**Do not confuse the components:** the copilot is the app; MCP is the tool protocol; a plugin is the installable package that references an MCP server; Docker packages the server; Cloud Run hosts the container and gives it an HTTPS URL. Publishing into a plugin directory requires separate submission, domain checks and approval.

## Reuses *actual* project evidence

`artifacts/holdout_offer_scoring.csv` and `artifacts/metrics.json` are original **CardGrowth AI Project 3** outputs. They contain **8,000 synthetic prospects**, original offer-response estimates and randomized assignment outcomes, not commercial data. Outputs are reproducible through the original CardGrowth pipeline; the copied artifacts are frozen snapshots for a fast server.

| Tool | Question it answers | Verified baseline |
|---|---|---|
| `diagnose_growth` | Where are funnel bottlenecks? | Standard 11.59%, cash-flow 14.35%, rewards 13.13% conversion |
| `analyze_segments` | How do segment predictions differ? | Outputs predicted effects, not causal estimates |
| `simulate_pricing` | What if a **uniform** annual fee changes? | Hypothetical elasticity and first-year contribution |
| `optimize_campaign` | How should a constrained marketing budget be allocated? | 2,600 contacts, $2,290.80 spending, $50,146.84 predicted value |
| `evaluate_experiment` | How strong is A/B conversion evidence? | Cash-flow +2.77 percentage points, unadjusted p≈0.0027 |

**Critical caveat:** The original CardGrowth project estimated $50,147 in model-predicted incremental first-year contribution, but its synthetic simulator gave ~$23,484 expected value and the randomized off-policy estimate was too uncertain to establish positive returns. DecisionIQ exposes that disagreement, not just the most flattering figure.

## Start the working web MVP

From the project root, Python 3.11+:

```bash
python -m pip install -r requirements-local.txt
python -m unittest discover -s tests -v
uvicorn main:app --reload --port 8080
```

Open **http://localhost:8080**. Use the suggestions, free-text questions, or scenario sliders. The public demo runs without credentials or a paid model. `requirements-local.txt` excludes MCP for environments where that optional package is not installed.

Health check: `GET /health`; tool metadata: `GET /api/catalog`.

```bash
curl -s http://localhost:8080/api/tools/optimize_campaign \
  -H 'Content-Type: application/json' \
  -d '{"arguments":{"budget":1500,"max_contacts":2600}}'
```

## Enable **real frontier API** reasoning

Install production dependencies, including the MCP SDK where available:

```bash
pip install -r requirements.txt
export ENABLE_LLM=1
export OPENAI_MODEL=gpt-6  # substitute an available model for your API account
export OPENAI_API_KEY='YOUR_PRIVATE_API_KEY'
export COPILOT_ACCESS_TOKEN='GENERATE_A_LONG_RANDOM_PRIVATE_TOKEN'
uvicorn main:app --port 8080
```

Visit the site; it detects frontier mode and displays a password/token input. Your model key is server-only. Only the token goes in the browser request header; it is not persisted to localStorage. This is a demo access gate, **not a production identity system**. Add per-user authorization, edge rate limiting, cost caps, abuse monitoring and durable billing before allowing broad AI API access.

Frontier mode uses `POST https://api.openai.com/v1/responses` with function calling. Each tool call is validated against strict Pydantic input ranges, run by your Python code, then returned to the model. A bounded tool loop (max 4 rounds) avoids unlimited requests. A mocked function-calling round-trip is covered in unit tests; a **live billable API call was not made**.

## Deploy the free public website + API

Docker:

```bash
docker build -t decisioniq .
docker run --rm -p 8080:8080 -e ENABLE_LLM=0 -e ENABLE_MCP=0 decisioniq
```

Cloud Run from source (Google Cloud credentials, billing and project required):

```bash
gcloud run deploy decisioniq-copilot \
  --source . --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENABLE_LLM=0,ENABLE_MCP=0
```

This publishes the *synthetic free public demo* at a Cloud Run URL. Deploying is a user-side action; the project has **not** been deployed through this chat. See `docs/DEPLOYMENT.md` for live API secrets and MCP setup.

## ChatGPT/Codex plugin path

See `docs/PLUGIN.md` and `plugin-template/`. Once you have a real, HTTPS-hosted `/mcp` endpoint, generate a **draft** package:

```bash
python scripts/prepare_plugin.py \
  --mcp-url https://YOUR-ACTUAL-DEPLOYED-HOST/mcp \
  --out DecisionIQ_Plugin_Template.zip
```

The tool refuses placeholder domains; this ZIP is a developer draft, **not a published or approved plugin**. To publish, supply valid publisher metadata, assets, privacy/support pages, domain verification and review materials to the current plugin-directory submission flow.

## What makes this senior-BA level

1. **Problem framing:** optimize acquisition *contribution*, not just click/apply rates.
2. **Counterfactual thinking:** distinguish observed randomized conversion from uncertain policy economics.
3. **Product economics:** quantify first-year margin under hypothetical annual fee/rewards trade-offs.
4. **Decision constraints:** subject offer selection to budget/contact capacity; explain why greedy is not guaranteed optimal.
5. **Governance:** tool-level evidence, explicit uncertainty, no individual credit decisions, synthetic-only public demo.
6. **Product execution:** API contract, UI, Docker, optional MCP adapter, deployment, integration/unit checks.

## Reproducibility and validation

`python -m unittest discover -s tests -v` checks 22+ tool, web, and mocked function-call behaviors. Numeric outputs are deterministic because precomputed CardGrowth artifacts are included.

**Validated here:** backend and frontend static render, tool calls, HTTP unit/integration tests, browser interaction with mocked HTTP responses, and JavaScript syntax.

**Not validated:** a live OpenAI API call, a built Docker container, public Google Cloud deployment, real MCP handshake, security penetration test, domain verification, or plugin-directory approval.

## Project layout

```
decisioniq_copilot/
├── main.py                      # FastAPI backend, optional MCP ASGI mount
├── decisioniq/
│   ├── tools.py                 # five Pydantic-validated deterministic tools
│   ├── agent.py                 # offline route + Responses API function-call loop
│   └── mcp_integration.py       # optional official MCP v2 adapter
├── web/                         # responsive browser-based DecisionIQ workspace
├── artifacts/                   # frozen synthetic CardGrowth test data + metrics
├── src/                         # reused original CardGrowth financial/experiment logic
├── plugin-template/             # portable plugin manifest + decision workflow skill
├── scripts/prepare_plugin.py    # draft plugin package generator after deployment
├── tests/                       # no-paid-API reproducibility checks
├── docs/                        # architecture, deployment, product evaluation, preview
├── Dockerfile
└── requirements*.txt
```

This is an educational portfolio product, not banking software. Never upload client records or real prospect/credit data into the public app. Credit risk, adverse-action, fair-lending, security and privacy reviews would be mandatory for any real issuer integration.
