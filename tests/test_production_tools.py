import importlib.util,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];TOOLS=ROOT/'skills/video-production-tools'
class ToolsFlow(unittest.TestCase):
 def setUp(self):
  self.area=tempfile.TemporaryDirectory(prefix='workflow-tools-');self.r=Path(self.area.name);self.lib=self.r/'library';self.project=self.r/'project';self.project.mkdir();self.env={**os.environ,'OMM_ASSET_CONFIG':str(self.r/'no-config.json')}
  self.run_cli('video_library.py','--library',self.lib,'init')
  self.video=self.r/'source.mp4';self.audio=self.r/'tone.mp3'
  subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','testsrc2=s=160x90:r=10:d=2','-f','lavfi','-i','sine=frequency=400:duration=2','-shortest','-c:v','libx264','-c:a','aac',str(self.video)],check=True,capture_output=True)
  subprocess.run(['ffmpeg','-v','error','-i',str(self.video),'-vn',str(self.audio)],check=True,capture_output=True)
 def tearDown(self):self.area.cleanup()
 def run_cli(self,entry,*args,expect=0):
  p=subprocess.run([sys.executable,str(ROOT/entry),*map(str,args)],cwd=self.r,env=self.env,capture_output=True,text=True,timeout=60);self.assertEqual(p.returncode,expect,p.stdout+p.stderr);return p
 def tool(self,*args,expect=0):return self.run_cli('video_tools.py','--library',self.lib,*args,expect=expect)
 def test_product_cards_publish_find_and_action_gate(self):
  opened=json.loads(self.tool('cards','intake','--project',self.project,'--file',self.video,'--role','product_ui_original','--product-name','测试夹具','--provenance','本次合成非真实UI','--inspection-scope','仅验证协议').stdout)
  path=Path(opened['segmentCards']);j=json.loads(path.read_text());j['segments']=[{'id':'test','title':'测试面板','observed':'仅合成夹具声明','keywords':['测试面板'],'status':'structure_reviewed','reviewScope':'sampled_frames','startSeconds':0,'endSeconds':1,'keyframesSeconds':[0,.5],'sampledSeconds':[0,.5]}];path.write_text(json.dumps(j,ensure_ascii=False))
  self.tool('cards','publish','--cards',path);found=json.loads(self.tool('cards','find','测试面板').stdout);self.assertEqual(found['count'],1)
  j['segments'][0].update(status='action_reviewed',action='点击',beforeState='前态',afterState='后态');path.write_text(json.dumps(j));self.tool('cards','publish','--cards',path,expect=1)
 def test_local_analysis_and_cache_without_cloud_calls(self):
  out=self.r/'analysis';self.tool('analyze','--source',self.video,'--out',out,'--cloud','none',expect=1)
  result=json.loads(next(out.glob('*/analysis.json')).read_text());self.assertEqual(result['semanticStatus'],'model_candidates_not_human_approved');self.assertTrue(next(out.glob('*/precision.json')).is_file());self.assertTrue(next(out.glob('*/evidence.html')).is_file())
  self.assertTrue(all(x['status']=='needs_cloud_authorization' for x in result['windows']))
 def test_standalone_local_analysis_does_not_require_or_create_a_library(self):
  out=self.r/'standalone-analysis'
  self.run_cli('video_tools.py','analyze','--source',self.video,'--out',out,'--cloud','none',expect=1)
  result=json.loads(next(out.glob('*/analysis.json')).read_text())
  self.assertEqual(result['sourceLibraryLookup']['match'],'not_checked')
  self.assertEqual(result['executionStatus'],'incomplete')
  self.assertTrue(next(out.glob('*/precision.json')).is_file())
  self.assertEqual(list(out.rglob('*.sqlite')),[])
 def test_standalone_analysis_does_not_bypass_invalid_shared_config_or_submit(self):
  config=Path(self.env['OMM_ASSET_CONFIG']);config.write_text('{}')
  out=self.r/'invalid-config-analysis';self.run_cli('video_tools.py','analyze','--source',self.video,'--out',out,'--cloud','none',expect=1)
  self.assertEqual(list(out.rglob('analysis.json')),[])
  self.assertIn('已有统一库配置无效',(out/'batch-status.json').read_text())
  config.unlink();out=self.r/'submit-without-library'
  self.run_cli('video_tools.py','analyze','--source',self.video,'--out',out,'--cloud','none','--submit',expect=1)
  self.assertEqual(list(out.rglob('analysis.json')),[])
  self.assertEqual(list(out.rglob('*.sqlite')),[])
 def test_voice_style_cache_integrity_no_paid_requests(self):
  p=TOOLS/'voice/scripts/voiceover_cli.py';spec=importlib.util.spec_from_file_location('test_voice',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  registry=m.load_json(m.REGISTRY_PATH);style=registry['styles'][0];cache=self.r/'cache';output=self.r/'voice.mp3'
  with patch.object(m,'call_doubao_api',return_value=self.audio.read_bytes()) as mocked:
   one=m.synthesize_one('测试文本',style,registry,'',output,cache,False);two=m.synthesize_one('测试文本',style,registry,'',output,cache,False)
   self.assertFalse(one['cache_hit']);self.assertTrue(two['cache_hit']);self.assertEqual(mocked.call_count,1)
   next(cache.glob('*.mp3')).write_bytes(b'corrupt')
   with self.assertRaises(ValueError):m.synthesize_one('测试文本',style,registry,'',output,cache,False)
   self.assertEqual(mocked.call_count,1)
 def test_music_select_and_reject_changed_license(self):
  e=self.r/'license.txt';e.write_text('本次合成测试声音自有声明，非外部许可')
  self.tool('music','add','--file',self.audio,'--title','calm fixture','--license-file',e,'--rights','owned','--source-url','https://example.invalid/synthetic','--tags','calm')
  plan=self.r/'music.json';self.tool('music','plan','--query','calm','--seconds',1,'--out',plan);j=json.loads(plan.read_text());self.assertEqual(j['status'],'selected_not_mixed');self.assertEqual(j['reason'],'literal_tag_match')
  Path(j['selected']['licenseEvidence']).write_text('changed');self.tool('music','plan','--query','calm','--seconds',1,'--out',self.r/'bad.json',expect=1)
 def test_ledger_snapshot_rollback_and_actual_unmarked_comparison(self):
  self.run_cli('video_make.py','init','--project',self.r/'film','--brief','测试夹具');self.project=self.r/'film';script=self.r/'script.txt';script.write_text('甲乙');self.run_cli('video_make.py','lock-script','--project',self.project,'--file',script,'--origin','agent_authored_for_requested_task')
  self.run_cli('video_make.py','add-asset','--project',self.project,'--id','clip','--file',self.video,'--kind','video','--origin','project_authored','--source','FFmpeg夹具','--rights','owned','--basis','本次合成')
  p=self.project/'workflow/plan.json';j=json.loads(p.read_text());j['shots']=[{'id':'S01','asset':'clip','duration':1},{'id':'S02','asset':'clip','duration':1}];p.write_text(json.dumps(j));base=self.project/'base.mp4';base.write_bytes(self.video.read_bytes());candidate=self.project/'candidate.mp4';candidate.write_bytes(self.video.read_bytes());e=self.project/'feedback.txt';e.write_text('测试修改合同，仅允许S01，非真实用户反馈')
  self.tool('ledger','--project',self.project,'init');snap=json.loads(self.tool('ledger','--project',self.project,'snapshot').stdout)
  self.tool('ledger','--project',self.project,'protect','--shots','S01','--baseline','base.mp4','--evidence','feedback.txt');self.tool('ledger','--project',self.project,'verify','--candidate','candidate.mp4')
  j['shots'][1]['duration']=.5;p.write_text(json.dumps(j));self.tool('ledger','--project',self.project,'verify','--candidate','candidate.mp4',expect=1)
  self.tool('ledger','--project',self.project,'rollback','--snapshot',snap['snapshot']);self.assertEqual(json.loads(p.read_text())['shots'][1]['duration'],1)
  self.tool('ledger','--project',self.project,'decision','--file','candidate.mp4','--status','rejected','--by','test fixture','--scope','全片','--reason','测试拒收','--evidence','feedback.txt');self.tool('ledger','--project',self.project,'verify','--candidate','candidate.mp4',expect=1)
 def test_cloud_inference_request_and_candidate_parsing_mock_only(self):
  import time
  sys.path.insert(0,str(TOOLS/'analysis'));spec=importlib.util.spec_from_file_location('analysis_fixture',TOOLS/'analysis/pipeline.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.PROJECT='fixture-project';m.ENDPOINT='https://example.invalid/model';m._TOKEN='synthetic-test-token';m._TOKEN_TIME=time.monotonic()
  response={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps({'visual':[{'start':0,'end':1,'description':'synthetic fixture'}],'sfx':[],'sync':[]})}]}}],'usageMetadata':{'promptTokenCount':1,'candidatesTokenCount':1}}
  class Reply:
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def read(self):return json.dumps(response).encode()
  with patch('urllib.request.urlopen',return_value=Reply()) as net:
   result,warnings=m.infer(self.video,'video',2,self.r/'attempt.json');self.assertEqual(net.call_count,1);self.assertEqual(result['visual'][0]['status'],'model_candidate')
  self.assertIn('usageMetadata',json.loads((self.r/'attempt.json').read_text()))
 def test_visual_contract_and_empty_evidence_are_not_approval(self):
  workflow=self.project/'workflow';workflow.mkdir();(workflow/'plan.json').write_text(json.dumps({'shots':[{'id':'S01','event':'测试动作'}]}))
  self.tool('contract','--project',self.project,'init');self.tool('contract','--project',self.project,'check',expect=1)
  p=workflow/'visual-reference-contract.json';d=json.loads(p.read_text());d['visualWorld']['continuityMechanism']='同一对象';d['visualWorld']['colorSource']['evidence']='测试原创依据';d['referencePolicy']['originalReason']='本次仅测试字段';p.write_text(json.dumps(d));self.tool('contract','--project',self.project,'check')
  evidence=self.project/'evidence.json';evidence.write_text(json.dumps({'schemaVersion':1,'lockedStoryboard':'workflow/plan.json','sources':[],'shots':[]}));self.tool('evidence',evidence,'--workspace-root',self.project,'--require-ready',expect=1)
 def test_music_apply_and_unknown_cost(self):
  e=self.r/'license.txt';e.write_text('仅合成夹具自有声明');self.tool('music','add','--file',self.audio,'--title','calm fixture','--license-file',e,'--rights','owned','--source-url','https://example.invalid/test','--tags','calm');selection=self.r/'selection.json';self.tool('music','plan','--query','calm','--seconds',1,'--out',selection)
  w=self.project/'workflow';w.mkdir();(self.project/'assets').mkdir();(w/'brief.json').write_text('{}');(w/'assets.json').write_text(json.dumps({'assets':[]}));(w/'plan.json').write_text(json.dumps({'shots':[{'duration':1}],'audio':{'mode':'silent','tracks':[]}}));self.tool('music','apply','--project',self.project,'--selection',selection);self.assertEqual(json.loads((w/'plan.json').read_text())['audio']['tracks'][0]['role'],'bgm');self.assertEqual(json.loads((w/'assets.json').read_text())['assets'][0]['rights']['status'],'owned')
  manifest=self.r/'manifest.json';manifest.write_text(json.dumps({'generated':[{'provider':'doubao','request_hash':'fixture','cache_hit':False,'quality':{'duration_seconds':2}}]}));price=self.r/'prices.json';price.write_text('{}');out=json.loads(self.tool('music','cost','--manifest',manifest,'--prices',price).stdout);self.assertIsNone(out['items'][0]['estimatedCost'])
if __name__=='__main__':unittest.main()
