"""Distribution integrity and useful source export; no existing media or DB used."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'skills/video-motion-kit'


class MotionFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.area = tempfile.TemporaryDirectory(prefix='motion-kit-tests-')
        cls.root = Path(cls.area.name)
        cls.skill = cls.root/'standalone motion kit'
        shutil.copytree(SOURCE, cls.skill, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        cls.cli = cls.skill/'scripts/motion.py'

    @classmethod
    def tearDownClass(cls):
        cls.area.cleanup()

    def call(self, *args, expect=0):
        p = subprocess.run([sys.executable, '-B', str(self.cli), *map(str,args)], cwd=self.root,
                           env={**os.environ, 'OMM_ASSET_CONFIG': str(self.root/'not-a-production-config.json')},
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, expect, p.stdout+p.stderr)
        return json.loads(p.stdout if not expect else p.stderr)

    def out(self):
        return self.root/next(tempfile._get_candidate_names())

    def test_standalone_stats_search_and_exact_resolution(self):
        stats=self.call('stats');self.assertEqual(stats['entries'],363)
        self.assertEqual(stats['byRuntime'],{'web_react_interaction':202,'remotion':161})
        results=self.call('search','数字','--runtime','remotion','--no-media')
        self.assertGreater(len(results['results']),0)
        r=self.call('resolve','odometer-digit-roll')
        self.assertIn('OdometerDigitRoll.tsx',str(r['entry']['demos']))
        self.assertTrue(r['recipeText'].strip())

    def test_full_file_audit_excludes_media(self):
        r=self.call('audit');self.assertEqual(r['state'],'audit_pass');self.assertEqual(r['mediaFiles'],0)
        self.assertEqual(r['entriesNeedingNewMedia'],21)

    def test_web_export_has_local_helpers_and_license(self):
        catalog=json.loads((self.skill/'references/catalog.json').read_text())['entries']
        entry=next(e for e in catalog if e['provider']=='MotionVault' and any('src/hooks/useInView' in f for f in e['files']))
        out=self.out();r=self.call('export',entry['id'],'--out',out)
        self.assertFalse(r['mediaIncluded'])
        self.assertTrue((out/'vendor/motionvault/src/hooks/useInView.ts').is_file())
        self.assertTrue((out/'vendor/motionvault/LICENSE').is_file())
        text=(out/'MOTION-SOURCE.json').read_text();self.assertNotIn('/Users/',text)
        self.assertIn('拒绝覆盖',self.call('export',entry['id'],'--out',out,expect=1)['error'])

    def test_scaffold_exact_demo_preserves_source_and_dependencies(self):
        out=self.out();r=self.call('scaffold','slow-push-in','--demo','SlowPushIn.tsx','--out',out)
        self.assertEqual(r['component'],'SlowPushIn')
        self.assertFalse(r['dependenciesInstalled'])
        root=(out/'src/Root.tsx').read_text();self.assertIn('SlowPushIn',root)
        self.assertTrue((out/'motion-source/vendor/video-shotcraft/demos/_fixtures/Fixtures.tsx').is_file())
        self.assertTrue((out/'motion-source/vendor/video-shotcraft/LICENSE').is_file())

    def test_web_and_missing_media_cannot_masquerade_as_renderable(self):
        out=self.out()
        self.assertIn('网页交互',self.call('scaffold','MV:accordion-gallery','--out',out,expect=1)['error'])
        self.assertFalse(out.exists())
        self.assertIn('不含旧媒体',self.call('scaffold','ai-stream-response','--out',out,expect=1)['error'])
        self.assertFalse(out.exists())

    def test_corrupted_source_is_rejected_before_export(self):
        entry=self.call('resolve','odometer-digit-roll')['entry'];path=self.skill/entry['recipe']
        original=path.read_bytes()
        try:
            path.write_bytes(b'changed')
            self.assertIn('内容变更',self.call('resolve','odometer-digit-roll',expect=1)['error'])
        finally:
            path.write_bytes(original)

    def test_project_selection_keeps_version_and_rejects_escape(self):
        project=self.out();project.mkdir()
        self.call('record','odometer-digit-roll','--project',project,'--shot','S01','--mode','remix','--reason','为当前数据变化设计','--change','替换示例数字')
        ledger=json.loads((project/'workflow/motion-selection.json').read_text())
        self.assertTrue(ledger['selections'][0]['sourceVersion'])
        self.assertFalse(ledger['selections'][0]['userApproved'])
        outside=self.out();outside.mkdir();escaped=self.out();escaped.mkdir();(escaped/'workflow').symlink_to(outside)
        self.assertIn('越界',self.call('record','new-original','--mode','invent','--project',escaped,'--shot','S01','--reason','test',expect=1)['error'])


if __name__=='__main__':
    unittest.main()
