# Architecture and analytical boundaries

```mermaid
flowchart TD
  U[Business analyst / product strategist] --> W[Web app: accessible public demo]
  U --> H[ChatGPT/Codex via installable plugin, after review]
  W --> A[FastAPI container /api/chat]
  H --> M[Optional remote MCP adapter /mcp]
  A --> O{Mode}
  O -->|Offline default| D[Deterministic intent router]
  O -->|Token-gated and enabled| F[OpenAI Responses API]
  F --> T[Function call arguments]
  D --> B[Five read-only decision tools]
  T --> B
  M --> B
  B --> V[Pydantic validation / policy limits]
  V --> C[CardGrowth frozen holdout: 8k synthetic leads]
  V --> P[Original CardGrowth financial and experiment logic]
  P --> R[Computed result, numeric uncertainty, assumptions]
  C --> R
  R --> D
  R --> F
  R --> M
  R --> W
```

**Privacy:** no file upload, raw SQL execution, writes, automatic marketing actions or banking data. 

**Trust boundary:** an LLM can select only named functions with bounded numeric inputs. It cannot run arbitrary Python, control database queries, access customer accounts, or use bank systems. Tool output is evidence, not instructions. The frontend renders user-provided text as text and escapes the tool-grounded markdown response.

**Source of truth:** original CardGrowth Project 3 snapshot scores, not an invented new cohort. Model values are synthetic predictions; financial decisions would require causal pilot evidence and separately validated credit-risk economics.

**Technical debt for production:** live cloud/SDK integration tests, stronger token/auth provider, edge quotas, audit logs, robust structured output and trace validation, serverless MCP session strategy, privacy notices, publisher verification, and independent model governance.
