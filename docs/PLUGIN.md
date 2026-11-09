# From MCP adapter to an installable ChatGPT plugin

This repository includes a **template**, not a submitted plugin. It includes portable `plugin.json`, an MCP manifest placeholder and a reusable workflow skill. Packaging requires a real deployed MCP endpoint.

```bash
python scripts/prepare_plugin.py --mcp-url https://YOUR_REAL_HOST/mcp --out DecisionIQ_Plugin_Template.zip
```

The generated `mcp.json` points to the remote Streamable HTTP server. A ChatGPT host calls MCP analytical tools and supplies its *own* model reasoning—no second frontier API bill from DecisionIQ is needed for plugin-side usage. The standalone DecisionIQ web app can independently use the OpenAI Responses API when the private API option is enabled.

The **public plugin directory** requires validated MCP tooling, publisher/website/privacy/support metadata and assets, domain ownership verification, review cases, a video and approval. An installer cannot publicly install this until those steps have passed. Consult current documentation; packaging and directory schema evolve.

A directory reviewer should be able to verify that:
- Tool metadata accurately describes 5 synthetic read-only operations.
- Every response marks financial values as modeled and never claims realized revenue.
- Numeric bounds and no-customer-data policy are enforced server-side.
- Unauthorized personal credit decision requests do not trigger any action.
- Use of `/mcp` is governed by allowed host/origin settings and applicable authorization.

Resources: https://developers.openai.com/plugins/build/plugins and https://developers.openai.com/plugins/deploy/submission .
