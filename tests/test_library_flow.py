"""Synthetic temp files and real SQLite; no source assets or production DB."""
import hashlib,json,os,shutil,sqlite3,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class LibraryFlow(unittest.TestCase):
 def setUp(self):
  self.area=tempfile.TemporaryDirectory(prefix='own-library-test-');self.r=Path(self.area.name);self.lib=self.r/'my library';self.env={**os.environ,'OMM_ASSET_CONFIG':str(self.r/'no-existing-config.json'),'PYTHONDONTWRITEBYTECODE':'1'}
  self.source=self.r/'new input.dat';self.source.write_bytes(b'new synthetic input, not a reviewed product recording')
  self.call('init')
 def tearDown(self):self.area.cleanup()
 def call(self,*args,expect=0,env=None):
  p=subprocess.run([sys.executable,str(ROOT/'video_library.py'),'--library',str(self.lib),*map(str,args)],cwd=self.r,env=env or self.env,capture_output=True,text=True,timeout=30)
  self.assertEqual(p.returncode,expect,p.stdout+p.stderr);return json.loads(p.stdout if expect==0 else p.stderr)
 def ingest(self,**opts):
  args=['ingest','--file',str(self.source),'--title','测试参考','--kind','image','--category','对象接力','--use','交换位置构图']
  for k,v in opts.items():args+=['--'+k.replace('_','-'),str(v)]
  return self.call(*args)
 def test_new_empty_library_dedup_notes_versions_and_literal_retrieval(self):
  with sqlite3.connect(self.lib/'assets.sqlite') as c:self.assertEqual(c.execute('select count(*) from asset_records').fetchone()[0],0)
  one=self.ingest();two=self.ingest();self.assertEqual(one['assetId'],two['assetId']);self.assertTrue(two['notes']['replayed'])
  self.assertEqual(self.call('search','交换位置')['count'],1)
  note=self.r/'analysis.md';note.write_text('新观察：先交换，再落定。未检查声音。')
  self.ingest(analysis=note);item=self.call('get',one['assetId']);self.assertIn('先交换',item['catalogNotes']['analysis']);self.assertEqual(self.call('search','先交换')['count'],1)
  self.assertEqual(item['catalogNotes']['rights']['status'],'unknown')
  self.source.unlink();moved=self.r/'moved library';shutil.move(self.lib,moved);self.lib=moved
  item=self.call('get',one['assetId']);self.assertEqual(len(item['verifiedLocalFiles']),1);self.assertTrue(Path(item['verifiedLocalFiles'][0]['path']).is_file())
 def test_context_and_product_evidence_stay_separate(self):
  one=self.ingest(role='feedback');self.assertEqual(self.call('search','')['count'],0)
  self.assertEqual(self.call('search','','--include-context')['count'],1)
  denied=self.call('ingest','--file',self.source,'--title','假升级','--kind','image','--category','界面','--role','product-original','--product-name','测试产品','--provenance','测试声明非真实观看','--inspection','仅夹具',expect=1)
  self.assertIn('不同证据角色',denied['error']);self.assertEqual(self.call('search','','--scope','product-ui')['count'],0)
  self.assertIn('不能作为',self.call('get',one['assetId'],'--scope','product-ui',expect=1)['error'])
 def test_rights_archive_and_backup_boundaries(self):
  self.assertIn('依据',self.call('ingest','--file',self.source,'--title','测试','--kind','audio','--category','声音','--rights','licensed',expect=1)['error'])
  self.assertIn('归档',self.call('ingest','--file',self.source,'--title','样片','--kind','user_archived_video','--category','成片',expect=1)['error'])
  one=self.ingest();dest=self.r/'db-only.sqlite';b=self.call('backup','--out',dest);self.assertFalse(b['mediaBackedUp'])
  with sqlite3.connect(dest) as c:self.assertEqual(c.execute('pragma integrity_check').fetchone()[0],'ok');self.assertEqual(c.execute('select count(*) from asset_records').fetchone()[0],1)
 def test_existing_shared_configuration_blocks_parallel_init_and_invalid_write(self):
  cfg=self.r/'existing.json';cfg.write_text(json.dumps({'db':str(self.r/'existing.sqlite'),'cli':'existing-cli','readOnly':True}))
  env={**self.env,'OMM_ASSET_CONFIG':str(cfg)}
  new=self.r/'must-not-exist';p=subprocess.run([sys.executable,str(ROOT/'video_library.py'),'--library',str(new),'init'],env=env,cwd=self.r,capture_output=True,text=True)
  self.assertNotEqual(p.returncode,0);self.assertFalse(new.exists())
if __name__=='__main__':unittest.main()
