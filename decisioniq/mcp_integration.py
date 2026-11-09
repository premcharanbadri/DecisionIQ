"""Optional MCP v2 adapter. Deploy with ENABLE_MCP=1 and mcp>=2.

SDK integration requires live environment validation. Read-only synthetic tools only.
Host allowlist MUST be explicit for real deployments.
"""
import os
from decisioniq.tools import execute

def build_mcp_app():
    from mcp.server import MCPServer
    from mcp.server.transport_security import TransportSecuritySettings

    server=MCPServer('DecisionIQ Synthetic Strategy Tools')

    @server.tool()
    def diagnose_growth_tool(segment:str='All')->dict:
        """Compare randomized synthetic application, approval, activation funnel metrics. No real customer data."""
        return execute("diagnose_growth", {"segment":segment})

    @server.tool()
    def analyze_segments_tool(offer:str='All')->dict:
        """Evaluate synthetic customer segment conversion and modeled response estimates. Not a causal effect."""
        return execute("analyze_segments", {"offer":offer})

    @server.tool()
    def simulate_pricing_tool(annual_fee:float=0,conversion_penalty_per_100:float=.012,rewards_rate:float=.0012)->dict:
        """Simulate uniform annual-fee marketing economics. Does NOT personalize APR or decide creditworthiness."""
        return execute("simulate_pricing", {"annual_fee":annual_fee,"conversion_penalty_per_100":conversion_penalty_per_100,"rewards_rate":rewards_rate})

    @server.tool()
    def optimize_campaign_tool(budget:float=2600,max_contacts:int=2600,segment:str='All')->dict:
        """Compare constrained synthetic marketing allocation; model predictions are not realized savings."""
        return execute("optimize_campaign", {"budget":budget,"max_contacts":max_contacts,"segment":segment})

    @server.tool()
    def evaluate_experiment_tool(offer:str='Cash-flow experience')->dict:
        """Report randomized synthetic marketing A/B experiment uncertainty against Standard offer."""
        return execute("evaluate_experiment", {"offer":offer})

    raw=os.environ.get('MCP_ALLOWED_HOSTS','')
    if not raw:
        raise RuntimeError('MCP_ALLOWED_HOSTS must name allowed DNS hosts for ENABLE_MCP=1; include deployment hostname')
    hosts=[s.strip() for s in raw.split(',') if s.strip()]
    origins=[s.strip() for s in os.getenv('MCP_ALLOWED_ORIGINS','').split(',') if s.strip()]
    transport=TransportSecuritySettings(allowed_hosts=hosts,allowed_origins=origins)
    mcp_asgi=server.streamable_http_app(transport_security=transport)
    return server,mcp_asgi
