import argparse,base64,importlib.util,json,tempfile,subprocess,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
class GoogleMusic(unittest.TestCase):
 def setUp(self):
  self.area=tempfile.TemporaryDirectory(prefix='google-music-test-');self.r=Path(self.area.name);self.prompt=self.r/'prompt.txt';self.prompt.write_text('Original instrumental acoustic cue, no vocals.');self.audio=self.r/'fixture.mp3'
  subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=240:duration=1','-y',str(self.audio)],check=True,capture_output=True)
  spec=importlib.util.spec_from_file_location('google_music_fixture',ROOT/'skills/video-production-tools/scripts/music_google.py');self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
  self.a=argparse.Namespace(prompt_file=str(self.prompt),output_dir=str(self.r/'output'),auth='api-key',model='lyria-3-clip-preview',project_id='',dry_run=False)
 def tearDown(self):self.area.cleanup()
 def reply(self,vertex=False):
  data=base64.b64encode(self.audio.read_bytes()).decode();obj={'outputs':[{'type':'audio','mime_type':'audio/mpeg','data':data}]} if vertex else {'candidates':[{'finishReason':'STOP','content':{'parts':[{'inlineData':{'mimeType':'audio/mpeg','data':data}}]}}]}
  class Reply:
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def read(self):return json.dumps(obj).encode()
  return Reply()
 def test_key_route_verified_cache_redaction_and_corruption(self):
  with patch.object(self.m,'api_key',return_value='synthetic-test-secret'),patch.object(self.m.urllib.request,'urlopen',return_value=self.reply()) as net:
   one=self.m.generate(self.a);two=self.m.generate(self.a);self.assertEqual(one['newRequests'],1);self.assertEqual(two['newRequests'],0);self.assertEqual(net.call_count,1)
   self.assertIn('generativelanguage.googleapis.com',net.call_args.args[0].full_url)
   for p in (self.r/'output').glob('*.json'):self.assertNotIn('synthetic-test-secret',p.read_text())
   (self.r/'output'/one['audio']['file']).write_bytes(b'changed')
   with self.assertRaises(ValueError):self.m.generate(self.a)
   self.assertEqual(net.call_count,1)
 def test_vertex_route_does_not_require_api_key(self):
  self.a.auth='adc';self.a.project_id='fixture-project'
  with patch.object(self.m,'adc_token',return_value='synthetic-access-token'),patch.object(self.m,'api_key',side_effect=AssertionError('wrong route')),patch.object(self.m.urllib.request,'urlopen',return_value=self.reply(True)) as net:
   one=self.m.generate(self.a);self.assertEqual(one['state'],'completed');self.assertIn('/projects/fixture-project/',net.call_args.args[0].full_url)
 def test_uncertain_paid_request_is_not_automatically_repeated(self):
  with patch.object(self.m,'api_key',return_value='synthetic-test-secret'),patch.object(self.m.urllib.request,'urlopen',side_effect=TimeoutError) as net:
   with self.assertRaises(ValueError):self.m.generate(self.a)
   with self.assertRaises(ValueError):self.m.generate(self.a)
   self.assertEqual(net.call_count,1);self.assertEqual(json.loads((self.r/'output/generation.json').read_text())['state'],'uncertain')
if __name__=='__main__':unittest.main()
