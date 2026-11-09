"""Generate a *template* portable plugin ZIP after the MCP service has a real HTTPS URL.

Not a public directory submission; public directory also needs verified publisher,
privacy/support pages, artwork, review cases, demo video and human approval.
"""
import argparse,json,shutil,tempfile,zipfile
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mcp-url',required=True,help='Real public https://.../mcp endpoint')
    p.add_argument('--out',default='DecisionIQ_Plugin_Template.zip')
    args=p.parse_args()
    u=urlparse(args.mcp_url)
    if u.scheme!='https' or not u.hostname or not u.path.endswith('/mcp') or any(x in u.hostname.lower() for x in ('example','localhost','replace','invalid')) or u.hostname.endswith(('.test','.local')) or bool(u.username) or bool(u.password) or bool(u.fragment) or bool(u.query):
        p.error('Provide an actual public HTTPS URL ending in /mcp; do not use placeholders.')
    with tempfile.TemporaryDirectory() as tmp:
        dst=Path(tmp)/'decisioniq-strategy';shutil.copytree(ROOT/'plugin-template',dst)
        mcp=json.loads((dst/'mcp.json.template').read_text());mcp['mcpServers']['decisioniq']['url']=args.mcp_url
        (dst/'mcp.json').write_text(json.dumps(mcp,indent=2))
        (dst/'mcp.json.template').unlink()
        out=Path(args.out).resolve()
        with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for f in dst.rglob('*'):
                if f.is_file():z.write(f,arcname=str(f.relative_to(dst)))
    print('Created draft plugin at',out)
    print('NOT a published plugin: validate live MCP, add directory metadata + review requirements, submit for approval.')

if __name__=='__main__':main()
