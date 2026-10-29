"""Real encode/decode, input integrity and cold-directory recovery, not taste tests."""
import hashlib
import array
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'skills/video-making-kit'


class ProductionFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.area = tempfile.TemporaryDirectory(prefix='video-making-kit-tests-')
        cls.root = Path(cls.area.name)
        # Only this skill, not the repo or other plugins, is available to the CLI.
        cls.skill = cls.root / 'standalone skill with spaces'
        shutil.copytree(SOURCE, cls.skill, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        cls.cli = cls.skill / 'scripts/video_make.py'
        cls.image = cls.root / 'new test input.png'
        cls.video = cls.root / 'new test input.mp4'
        cls.audio = cls.root / 'new tone.wav'
        for dest, source, extra in (
            (cls.image, 'color=c=orange:s=320x180:d=1', ['-frames:v', '1']),
            (cls.video, 'testsrc2=s=320x180:r=10:d=1', ['-c:v', 'libx264']),
            (cls.audio, 'sine=frequency=440:sample_rate=48000:duration=2', []),
        ):
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', source, *extra, str(dest)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.area.cleanup()

    def setUp(self):
        self.project = self.root / ('project-' + next(tempfile._get_candidate_names()))
        self.call('init', '--brief', '合成测试夹具，不作为可交付创意视频')
        script = self.project / 'script.txt'; script.write_text('前一镜\n后一镜\n')
        self.call('lock-script', '--file', script, '--origin', 'agent_authored_for_requested_task')
        for aid, kind, file in (('image', 'image', self.image), ('clip', 'video', self.video), ('tone', 'audio', self.audio)):
            self.call('add-asset', '--id', aid, '--file', file, '--kind', kind, '--origin', 'project_authored',
                      '--source', 'FFmpeg合成测试fixture', '--rights', 'owned', '--basis', '由测试代码本地生成')
        self.plan = json.loads((self.project / 'workflow/plan.json').read_text())
        self.plan.update(canvas={'width': 320, 'height': 180, 'fps': 10}, visualDirection='测试编解码', paletteBasis='FFmpeg测试色')
        self.plan['shots'] = [
            dict(id='S01', duration=1, scriptRange=[0, 3], asset='image', event='静图慢推', focus='色块',
                 acceptance='不丢帧', connection='切到测试图', zoom=[1, 1.1]),
            dict(id='S02', duration=1, scriptRange=[4, 7], asset='clip', event='测试图移动', focus='测试图',
                 acceptance='取足1秒', connection='结束', **{'in': 0}),
        ]
        self.plan['audio'] = {'mode': 'mix', 'reason': '合成音轨检查，不代表音乐质量', 'tracks': [
            {'asset': 'tone', 'role': 'test_signal', 'at': 0, 'in': 0, 'duration': 2, 'gainDb': -6, 'fadeIn': .1, 'fadeOut': .2},
            {'asset': 'tone', 'role': 'second_track', 'at': 1, 'in': .2, 'duration': .5, 'gainDb': -12, 'fadeIn': .1, 'fadeOut': .1}]}
        self.save()

    def save(self):
        (self.project / 'workflow/plan.json').write_text(json.dumps(self.plan, ensure_ascii=False, indent=2) + '\n')

    def call(self, command, *args, expect=0):
        result = subprocess.run([sys.executable, '-B', str(self.cli), command, '--project', str(self.project), *map(str,args)],
                                cwd=self.root, capture_output=True, text=True, timeout=90)
        self.assertEqual(result.returncode, expect, result.stdout + result.stderr)
        return json.loads(result.stdout if expect == 0 else result.stderr)

    def test_real_render_check_and_recover_without_original_paths(self):
        self.call('validate')
        self.call('render', '--out', 'out/candidate-r01.mp4')
        report = self.call('check', '--file', 'out/candidate-r01.mp4')
        self.assertEqual(report['decodedFrames'], 20)
        self.assertTrue(report['audio']['present'])
        old = self.project
        self.project = self.root / ('moved project ' + old.name)
        shutil.copytree(old, self.project)
        shutil.rmtree(old)
        self.call('render', '--out', 'out/recovered-r01.mp4')
        self.call('check', '--file', 'out/recovered-r01.mp4')
        self.assertEqual(hashlib.sha256((self.project/'out/candidate-r01.mp4').read_bytes()).hexdigest(),
                         hashlib.sha256((self.project/'out/recovered-r01.mp4').read_bytes()).hexdigest())

    def test_changed_asset_and_script_are_rejected(self):
        ledger = json.loads((self.project/'workflow/assets.json').read_text())
        asset = self.project / ledger['assets'][0]['path']
        original = asset.read_bytes(); asset.write_bytes(b'changed')
        self.assertIn('素材缺失或内容变更', self.call('validate', expect=1)['error'])
        asset.write_bytes(original)
        (self.project/'workflow/script.locked.txt').write_text('changed')
        self.assertIn('锁定脚本已变更', self.call('validate', expect=1)['error'])

    def test_short_leading_voice_and_end_aligned_second_track_finish(self):
        # Real film regression: first track ends early; second track reaches the
        # exact film boundary. Unbounded apad after amix did not terminate on
        # FFmpeg 9 for this ordering, despite output -t and downstream atrim.
        self.plan['audio']['tracks'] = [
            {'asset': 'tone', 'role': 'short_leading_voice', 'at': .3, 'in': 0, 'duration': 1, 'gainDb': -6},
            {'asset': 'tone', 'role': 'end_aligned_effect', 'at': 0, 'in': 0, 'duration': 2, 'gainDb': -12},
        ]
        self.save()
        self.call('render', '--out', 'out/end-aligned.mp4')
        report = self.call('check', '--file', 'out/end-aligned.mp4')
        self.assertEqual(report['decodedFrames'], 20)
        pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(self.project/'out/end-aligned.mp4'),
                              '-ss', '1.8', '-t', '0.1', '-vn', '-f', 's16le', '-ac', '1', '-ar', '48000', '-'],
                             check=True, capture_output=True, timeout=10).stdout
        samples = array.array('h'); samples.frombytes(pcm)
        self.assertGreater(len(samples), 4000)
        self.assertGreater(sum(s*s for s in samples)/len(samples), 10000,
                           'The end-aligned second track must remain audible after the first track ends')

    def test_script_gaps_and_video_audio_overruns_are_rejected(self):
        self.plan['shots'][1]['scriptRange'] = [4, 5]; self.save()
        self.assertIn('遗漏', self.call('validate', expect=1)['error'])
        self.plan['shots'][1]['scriptRange'] = [4, 7]
        self.plan['shots'][1]['in'] = .5; self.save()
        self.assertIn('越界', self.call('validate', expect=1)['error'])
        self.plan['shots'][1]['in'] = 0
        self.plan['audio']['tracks'][0]['in'] = 1; self.save()
        self.assertIn('越界', self.call('validate', expect=1)['error'])

    def test_outside_paths_and_overwrite_are_rejected(self):
        self.assertIn('越出', self.call('render', '--out', '../escape.mp4', expect=1)['error'])
        self.call('render', '--out', 'out/candidate.mp4')
        self.assertIn('拒绝覆盖', self.call('render', '--out', 'out/candidate.mp4', expect=1)['error'])
        self.assertIn('拒绝覆盖', self.call('init', '--brief', 'overwrite', expect=1)['error'])

    def test_symlink_asset_escape_is_rejected(self):
        external = self.root / 'outside.png'; shutil.copyfile(self.image, external)
        (self.project/'assets/escape.png').symlink_to(external)
        ledgerpath = self.project/'workflow/assets.json'; ledger = json.loads(ledgerpath.read_text())
        ledger['assets'][0]['path'] = 'assets/escape.png'; ledgerpath.write_text(json.dumps(ledger))
        self.assertIn('越出', self.call('validate', expect=1)['error'])

    def test_silent_plan_and_image_overlay(self):
        self.plan['audio'] = {'mode': 'silent', 'reason': '显式静音测试', 'tracks': []}
        self.plan['shots'][0]['layers'] = [{'asset': 'image', 'start': .2, 'end': .8, 'fadeIn': .1, 'fadeOut': .1}]
        self.save(); self.call('render', '--out', 'out/silent.mp4')
        report = self.call('check', '--file', 'out/silent.mp4')
        self.assertFalse(report['audio']['present'])
        data = bytearray((self.project/'out/silent.mp4').read_bytes()); data[-1] ^= 1
        (self.project/'out/silent.mp4').write_bytes(data)
        self.assertIn('回执不一致', self.call('check', '--file', 'out/silent.mp4', expect=1)['error'])


if __name__ == '__main__':
    unittest.main()
