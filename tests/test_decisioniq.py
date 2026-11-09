import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from decisioniq.tools import execute, data, openai_tools
from decisioniq.agent import demo_chat, frontier_chat
from main import app

class ToolsTest(unittest.TestCase):
    def test_holdout_integrity(self):
        d,m,p=data()
        self.assertEqual(len(d),8000)
        self.assertEqual(p.shape,(8000,3))
        self.assertEqual(d.lead_id.nunique(),8000)
    def test_initial_funnel_counts(self):
        r=execute('diagnose_growth',{})
        by={x['offer']:x for x in r['funnel_by_offer']}
        self.assertEqual(by['Standard']['prospects'],2719)
        self.assertEqual(by['Cash-flow experience']['applications'],372)
        self.assertEqual(by['Rewards experience']['prospects'],2689)
    def test_segment_filter(self):
        r=execute('diagnose_growth',{'segment':'Growth-focused'})
        self.assertEqual(len(r['funnel_by_offer']),3)
        self.assertLess(sum(x['prospects'] for x in r['funnel_by_offer']),8000)
    def test_invalid_params_rejected(self):
        for name,args in [('simulate_pricing',{'annual_fee':-20}),('optimize_campaign',{'budget':-1}),('diagnose_growth',{'segment':'invalid'}),('optimize_campaign',{'max_contacts':99999})]:
            with self.assertRaises(Exception):execute(name,args)
    def test_unknown_tool_rejected(self):
        with self.assertRaises(ValueError):execute('exec_python',{'code':'rm -rf /'})
    def test_baseline_policy_reproduces_cardgrowth(self):
        r=execute('optimize_campaign',{})
        self.assertEqual(r['policy']['contacts'],2600)
        self.assertAlmostEqual(r['policy']['spend_usd'],2290.8,places=1)
        self.assertAlmostEqual(r['policy']['model_predicted_incremental_first_year_contribution_usd'],50146.84,places=1)
    def test_spend_constraint(self):
        for budget in (0,100,1500):
            r=execute('optimize_campaign',{'budget':budget,'max_contacts':200})
            self.assertLessEqual(r['policy']['spend_usd'],budget+0.01)
            self.assertLessEqual(r['policy']['contacts'],200)
    def test_cashflow_experiment(self):
        r=execute('evaluate_experiment',{})
        self.assertEqual(r['counts']['control_applications'],315)
        self.assertEqual(r['counts']['treatment_applications'],372)
        self.assertTrue(r['two_offer_bonferroni_significant_at_fwer_5pct'])
        self.assertAlmostEqual(r['statistics']['absolute_percentage_point_lift'],2.767,places=2)
    def test_rewards_experiment_inconclusive(self):
        r=execute('evaluate_experiment',{'offer':'Rewards experience'})
        self.assertFalse(r['two_offer_bonferroni_significant_at_fwer_5pct'])
    def test_pricing_zero_change(self):
        r=execute('simulate_pricing',{})
        self.assertAlmostEqual(r['scenario_difference_usd'],0,places=1)
    def test_pricing_not_credit_apr(self):
        r=execute('simulate_pricing',{'annual_fee':100})
        self.assertIn('HYPOTHETICAL',r['status'])
        self.assertTrue(isinstance(r['scenario_difference_usd'],float))
    def test_json_schema_defs(self):
        tools=openai_tools()
        self.assertEqual(len(tools),5)
        self.assertTrue(all(t['type']=='function' for t in tools))
    def test_no_individual_credit_decision(self):
        r=demo_chat('Should we approve this applicant for a credit card?')
        self.assertEqual(r['trace'],[])
        self.assertIn('cannot decide',r['answer'])

    def test_offline_router_no_frontier(self):
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fake','ENABLE_LLM':'0'}):
            r=demo_chat('Budget $1200')
        self.assertEqual(r['mode'],'offline_demo')
        self.assertEqual(r['trace'][0]['tool'],'optimize_campaign')
        self.assertEqual(r['trace'][0]['result']['constraints']['budget_usd'],1200.)

class HttpTest(unittest.TestCase):
    def setUp(self):
        self.client=TestClient(app)
    def test_health_and_site(self):
        self.assertEqual(self.client.get('/health').status_code,200)
        r=self.client.get('/')
        self.assertEqual(r.status_code,200)
        self.assertIn('DecisionIQ',r.text)
    def test_catalog(self):
        r=self.client.get('/api/catalog')
        self.assertEqual(r.status_code,200)
        self.assertEqual(len(r.json()['tools']),5)
    def test_chat_offline(self):
        with patch.dict(os.environ,{'ENABLE_LLM':'0'}):
            r=self.client.post('/api/chat',json={'message':'Which offer has highest conversion?'})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()['mode'],'offline_demo')
    def test_invalid_http_tool(self):
        r=self.client.post('/api/tools/optimize_campaign',json={'arguments':{'budget':-100}})
        self.assertEqual(r.status_code,422)
    def test_no_live_api_without_access_token(self):
        with patch.dict(os.environ,{'ENABLE_LLM':'1','OPENAI_API_KEY':'test', 'COPILOT_ACCESS_TOKEN':'a_really_long_private_access_token'}):
            r=self.client.post('/api/chat',json={'message':'Optimize budget'})
        self.assertEqual(r.status_code,401)
    def test_live_not_enabled_with_weak_secret(self):
        with patch.dict(os.environ,{'ENABLE_LLM':'1','OPENAI_API_KEY':'test', 'COPILOT_ACCESS_TOKEN':'123'}):
            r=self.client.post('/api/chat',json={'message':'Optimize budget'})
        self.assertEqual(r.status_code,503)
    def test_input_limits(self):
        r=self.client.post('/api/chat',json={'message':'a'*1300})
        self.assertEqual(r.status_code,422)

class FakeAPIResponse:
    def __init__(self,body):self.body=body
    def raise_for_status(self):pass
    def json(self):return self.body

class FakeHTTPClient:
    def __init__(self,**kwargs):self.calls=0
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def post(self,url,headers,json):
        self.calls+=1
        if self.calls==1:
            assert json['tools'] and json['tool_choice']=='required' and not json['store']
            return FakeAPIResponse({'output':[{'type':'function_call','call_id':'c_1','name':'evaluate_experiment','arguments':'{"offer":"Cash-flow experience"}'}]})
        assert json['input'][-1]['type']=='function_call_output'
        return FakeAPIResponse({'output':[{'type':'message','content':[{'type':'output_text','text':'Synthetic lift is encouraging but not proof of profitable growth.'}]}]})

class PluginPackageUnitTest(unittest.TestCase):
    def test_draft_plugin_generator(self):
        import subprocess, tempfile, zipfile
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'plugin.zip'
            script=Path(__file__).resolve().parents[1]/'scripts'/'prepare_plugin.py'
            run=subprocess.run([sys.executable,str(script),'--mcp-url','https://decisioniq-prod.run.app/mcp','--out',str(target)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            with zipfile.ZipFile(target) as z:
                m=json.loads(z.read('mcp.json'))
                self.assertEqual(m['mcpServers']['decisioniq']['url'],'https://decisioniq-prod.run.app/mcp')
                self.assertIn('plugin.json',z.namelist())
                self.assertIn('skills/decision-strategy/SKILL.md',z.namelist())

class AgentUnitTest(unittest.TestCase):
    def test_function_call_cycle_without_paid_api(self):
        with patch.dict(os.environ,{'OPENAI_API_KEY':'dummy','OPENAI_MODEL':'gpt-6'}):
            with patch('decisioniq.agent.httpx.Client',FakeHTTPClient):
                r=frontier_chat('Is cash-flow better?')
        self.assertEqual(r['mode'],'frontier_api')
        self.assertEqual(r['trace'][0]['tool'],'evaluate_experiment')
        self.assertIn('not proof',r['answer'])

if __name__=='__main__':unittest.main()
