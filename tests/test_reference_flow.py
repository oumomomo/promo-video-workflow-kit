"""Real isolated media/SQLite tests; no production library or cloud calls."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]


class ReferenceFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.area = tempfile.TemporaryDirectory(prefix='reference-kit-test-')
        cls.root = Path(cls.area.name)
        cls.bundle = cls.root / 'portable bundle with spaces'
        shutil.copytree(PACKAGE, cls.bundle, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        cls.cli = cls.bundle / 'video_ref.py'
        cls.source = cls.root / 'white then black.mp4'
        subprocess.run([
            'ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=white:s=160x90:r=10:d=1',
            '-f', 'lavfi', '-i', 'color=black:s=160x90:r=10:d=1',
            '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=16000:duration=2',
            '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=0[v]', '-map', '[v]', '-map', '2:a',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(cls.source)
        ], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.area.cleanup()

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(dir=self.root, prefix='case-'))
        self.library = self.work / 'my library'
        self.env = {**os.environ, 'OMM_ASSET_CONFIG': str(self.work / 'no-shared-config.json'),
                    'PYTHONDONTWRITEBYTECODE': '1'}

    def cli_run(self, *args, expect=0, with_library=True, env=None):
        prefix = ['--library', str(self.library)] if with_library else []
        result = subprocess.run([sys.executable, str(self.cli), *prefix, *map(str, args)],
                                cwd=self.work, env=env or self.env, capture_output=True, text=True, timeout=45)
        self.assertEqual(result.returncode, expect, result.stderr + result.stdout)
        return json.loads(result.stdout if expect == 0 else result.stderr)

    def initialize(self):
        return self.cli_run('init', '--library', self.library, with_library=False)

    def prepare(self, **options):
        self.initialize()
        extra = []
        for key, value in options.items():
            extra.extend(['--' + key.replace('_', '-'), value])
        return self.cli_run('prepare', '--source', self.source, '--title', '测试镜头', *extra)

    def fill_notes(self, rid):
        path = self.work / 'notes.json'
        self.cli_run('notes', 'template', '--id', rid, '--out', path)
        notes = json.loads(path.read_text())
        notes.update(summary='亮暗切换：验证对象更新的前后顺序', inspection={
            'method': 'human_review', 'scope': '仅测试输入结构校验，不作为真实人工审阅记录',
            'observer': 'synthetic-test-fixture', 'date': 'fixture'})
        notes['phases'] = [{'start': 0, 'end': 2, 'observed': '测试声明：白色到黑色',
                            'inherit': '修改前后先后顺序', 'change': '换成本次内容', 'avoid': '不证明产品联动'}]
        path.write_text(json.dumps(notes, ensure_ascii=False))
        return path

    def test_prepare_notes_search_bind_and_usage(self):
        prepared = self.prepare(rights='owned', rights_evidence='本测试用FFmpeg生成')
        self.assertEqual(prepared['cloudCalls'], 0)
        self.assertGreaterEqual(prepared['candidateShots'], 2)
        evidence = Path(prepared['evidence'])
        self.assertGreaterEqual(len(list((evidence / 'frames').glob('*.jpg'))), 4)
        manifest = json.loads((evidence / 'manifest.json').read_text())
        self.assertEqual(manifest['audioStatus'], 'not_listened')
        rid = prepared['assetId']
        self.assertEqual(self.cli_run('search', '亮暗切换')['count'], 0)
        notes = self.fill_notes(rid)
        committed = self.cli_run('notes', 'submit', '--id', rid, '--file', notes)
        self.assertEqual(committed['state'], 'committed')
        self.assertFalse(committed['reviewChanged'])
        self.assertEqual(self.cli_run('search', '亮暗切换')['count'], 1)
        project = self.work / 'project'; project.mkdir()
        binding = self.cli_run('bind', '--project', project, '--shot', 'S01', '--id', rid,
                               '--start', 0, '--end', 1, '--inherit', '状态顺序', '--change', '业务内容', '--avoid', '虚构功能')
        ledger = json.loads(Path(binding['projectFile']).read_text())
        self.assertEqual(ledger['references'][0]['analysisVersion'], committed['version'])
        self.assertFalse(ledger['references'][0]['productCapabilityVerified'])
        self.assertIsNone(ledger['references'][0]['userApproval'])

    def test_cached_prepare_preserves_notes_and_rights(self):
        prepared = self.prepare(rights='owned', rights_evidence='FFmpeg测试源')
        rid = prepared['assetId']; notes = self.fill_notes(rid)
        first = self.cli_run('notes', 'submit', '--id', rid, '--file', notes)
        before = json.loads(notes.read_text())
        reused = self.cli_run('prepare', '--source', self.source, '--title', '另一次任务')
        self.assertEqual(reused['state'], 'reused')
        self.assertEqual(json.loads(notes.read_text()), before)
        again = self.cli_run('notes', 'submit', '--id', rid, '--file', notes)
        self.assertTrue(again['replayed']); self.assertEqual(first['version'], again['version'])
        exported = self.work / 'export.json'
        self.cli_run('export', '--id', rid, '--out', exported)
        data = json.loads(exported.read_text())
        mechanical = next(x for x in data['results'] if x['stream'] == 'mechanical-evidence')
        body = json.loads(mechanical['documents'][0]['body'])
        self.assertEqual(body['rightsDeclaration'], 'owned')

    def test_altered_evidence_is_rejected(self):
        prepared = self.prepare()
        manifest = Path(prepared['evidence']) / 'shots.json'
        manifest.write_text(manifest.read_text() + '\n')
        failed = self.cli_run('prepare', '--source', self.source, '--title', '测试镜头', expect=1)
        self.assertIn('哈希不匹配', failed['error'])

    def test_wrong_hash_or_outside_range_notes_are_rejected(self):
        rid = self.prepare()['assetId']; path = self.fill_notes(rid)
        notes = json.loads(path.read_text()); notes['sourceSha256'] = '0' * 64; path.write_text(json.dumps(notes))
        self.assertIn('相同原片', self.cli_run('notes', 'submit', '--id', rid, '--file', path, expect=1)['error'])
        notes['sourceSha256'] = hashlib.sha256(self.source.read_bytes()).hexdigest()
        notes['phases'][0]['end'] = 300; path.write_text(json.dumps(notes))
        self.assertIn('超出原片', self.cli_run('notes', 'submit', '--id', rid, '--file', path, expect=1)['error'])

    def test_unreviewed_notes_and_missing_notes_cannot_bind(self):
        rid = self.prepare()['assetId']; path = self.work / 'empty.json'
        self.cli_run('notes', 'template', '--id', rid, '--out', path)
        self.assertIn('观察方式', self.cli_run('notes', 'submit', '--id', rid, '--file', path, expect=1)['error'])
        project = self.work / 'project'; project.mkdir()
        self.cli_run('bind', '--project', project, '--shot', 'S01', '--id', rid,
                     '--start', 0, '--end', 1, '--inherit', '顺序', '--change', '内容', '--avoid', '虚构', expect=1)

    def test_shared_configuration_blocks_alternate_library(self):
        cfg = self.work / 'shared.json'; cfg.write_text(json.dumps({'db': 'production.sqlite', 'cli': 'original.py'}))
        env = {**self.env, 'OMM_ASSET_CONFIG': str(cfg)}
        result = self.cli_run('init', '--library', self.library, with_library=False, expect=1, env=env)
        self.assertIn('统一素材', result['error']); self.assertFalse(self.library.exists())

    def test_read_calls_use_configured_gateway(self):
        gateway = self.work / 'entry.py'
        gateway.write_text('import json,sys\nprint(json.dumps({"items":[],"count":0,"gatewayArgs":sys.argv[1:]}))\n')
        db = self.work / 'configured.sqlite'; db.write_bytes(b'gateway-test-only')
        cfg = self.work / 'shared.json'; cfg.write_text(json.dumps({'db': str(db), 'cli': 'original.py'}))
        env = {**self.env, 'OMM_ASSET_CONFIG': str(cfg)}
        result = self.cli_run('search', '测试', with_library=False, env=env)
        self.assertEqual(result['gatewayArgs'], ['search', '测试', '--kind', 'reference_video'])
        self.assertEqual(db.read_bytes(), b'gateway-test-only')

    def test_nonempty_directory_is_never_overwritten(self):
        self.library.mkdir(); original = self.library / 'keep.txt'; original.write_text('keep')
        self.cli_run('init', '--library', self.library, with_library=False, expect=1)
        self.assertEqual(original.read_text(), 'keep')

    def test_same_bytes_at_another_path_reuse_existing_evidence(self):
        first = self.prepare()
        copied = self.work / 'renamed.mp4'; shutil.copy2(self.source, copied)
        requested = self.work / 'another evidence directory'
        second = self.cli_run('prepare', '--source', copied, '--title', '另一次制作', '--out', requested)
        self.assertEqual(second['state'], 'reused')
        self.assertEqual(second['evidence'], first['evidence'])
        self.assertEqual(second['assetId'], first['assetId'])
        self.assertFalse(requested.exists())

    def test_unknown_rights_block_direct_media_use(self):
        rid = self.prepare()['assetId']; notes = self.fill_notes(rid)
        self.cli_run('notes', 'submit', '--id', rid, '--file', notes)
        project = self.work / 'project'; project.mkdir()
        result = self.cli_run('bind', '--project', project, '--shot', 'S01', '--id', rid,
                              '--start', 0, '--end', 1, '--inherit', '顺序', '--change', '内容',
                              '--avoid', '虚构', '--use', 'media', expect=1)
        self.assertIn('权利声明', result['error'])
        self.assertFalse((project / 'workflow/reference-uses.json').exists())

    def test_project_symlink_cannot_write_outside_project(self):
        rid = self.prepare()['assetId']; notes = self.fill_notes(rid)
        self.cli_run('notes', 'submit', '--id', rid, '--file', notes)
        project = self.work / 'project'; project.mkdir()
        outside = self.work / 'other-project'; outside.mkdir()
        try:
            (project / 'workflow').symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('此平台不能建立测试符号链接')
        result = self.cli_run('bind', '--project', project, '--shot', 'S01', '--id', rid,
                              '--start', 0, '--end', 1, '--inherit', '顺序', '--change', '内容', '--avoid', '虚构', expect=1)
        self.assertIn('项目之外', result['error'])
        self.assertFalse((outside / 'reference-uses.json').exists())

    def test_existing_product_identity_is_preserved(self):
        self.initialize()
        backend = self.bundle / 'skills/video-reference-kit/backend/scripts/asset-library.py'
        result = subprocess.run([sys.executable, str(backend), '--db', str(self.library / 'assets.sqlite'),
                                 'register', '--file', str(self.source), '--title', '保留原始名称',
                                 '--category', '保留原始分类', '--evidence-role', 'product_ui_original',
                                 '--product-name', 'SyntheticFixture', '--source-provenance', '测试生成',
                                 '--inspection-scope', '仅测试身份字段'], cwd=self.work, env=self.env,
                                capture_output=True, text=True, check=True)
        old = json.loads(result.stdout)
        new = self.cli_run('prepare', '--source', self.source, '--title', '不可覆盖原名')
        current = self.cli_run('get', new['assetId'])
        self.assertEqual(old['id'], current['id'])
        self.assertEqual(current['title'], '保留原始名称')
        self.assertEqual(current['category'], '保留原始分类')
        self.assertEqual(current['metadata']['evidenceRole'], 'product_ui_original')

    def test_video_without_audio_remains_explicitly_without_audio(self):
        self.initialize()
        mute = self.work / 'silent.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(self.source), '-an', '-c:v', 'copy', str(mute)],
                       check=True, capture_output=True)
        prepared = self.cli_run('prepare', '--source', mute, '--title', '无声音输入')
        manifest = json.loads((Path(prepared['evidence']) / 'manifest.json').read_text())
        self.assertEqual(manifest['audioStatus'], 'no_audio_stream')


if __name__ == '__main__':
    unittest.main()
