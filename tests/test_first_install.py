"""First-install isolation and no-secret/no-cloud boundaries, plus real CLI help routing."""
import importlib.util
import io
import json
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class FirstInstall(unittest.TestCase):
    def module(self, filename):
        spec = importlib.util.spec_from_file_location('first_install_' + filename, ROOT / filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_doctor_never_authenticates_or_prints_secret_values(self):
        module = self.module('video_setup.py')
        def output(command):
            if command == ['fixture-node', '--version']:
                return 'v20.0.0'
            if command == ['fixture-ffmpeg', '-hide_banner', '-encoders']:
                return ' V libx264'
            raise AssertionError('Unexpected command: ' + str(command))
        env = {'GEMINI_API_KEY': 'synthetic-private-key-value', 'DOUBAO_TTS_API_KEY': 'synthetic-doubao-value'}
        with patch.dict(os.environ, env, clear=True), patch.object(module.shutil, 'which', side_effect=lambda x: 'fixture-' + x), patch.object(module, 'command_output', side_effect=output):
            result = module.inspect_environment()
        encoded = json.dumps(result)
        self.assertNotIn('synthetic-private-key-value', encoded)
        self.assertNotIn('synthetic-doubao-value', encoded)
        self.assertEqual(result['cloudRequests'], 0)
        self.assertFalse(result['credentialsRead'])
        self.assertTrue(result['services']['googleMusicKey']['environmentVariableSet'])

    def test_missing_tools_fail_basic_but_not_python_only_library(self):
        module = self.module('video_setup.py')
        with patch.object(module.shutil, 'which', return_value=None), redirect_stdout(io.StringIO()):
            self.assertEqual(module.main(['doctor', '--feature', 'basic', '--json']), 1)
            self.assertEqual(module.main(['doctor', '--feature', 'library', '--json']), 0)

    def test_doctor_rejects_websockets14_which_lacks_proxy_parameter(self):
        module = self.module('video_setup.py')
        with patch.object(module.importlib.util, 'find_spec', return_value=object()), patch.object(module.importlib.metadata, 'version', return_value='14.2'):
            report = module.inspect_environment()
        self.assertFalse(report['features']['voice']['runtimeReady'])
        self.assertIn('websockets>=15,<17', report['features']['voice']['missing'])

    def test_subcommand_help_reaches_actual_voice_and_music_commands(self):
        for args, expected in [(['voice', 'synthesize', '--help'], '--style-id'),
                               (['music', 'generate', '--help'], '--prompt-file')]:
            result = subprocess.run([sys.executable, str(ROOT / 'video_tools.py'), *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(expected, result.stdout)

    def test_review_rejects_old_node_before_install_or_config(self):
        module = self.module('video_review.py')
        with patch.object(sys, 'argv', ['video_review.py', 'config']), patch.object(module.shutil, 'which', return_value='fixture-node'), patch.object(module.subprocess, 'check_output', return_value='v18.0.0'):
            with self.assertRaisesRegex(ValueError, 'Node.js 20'):
                module.main()


if __name__ == '__main__':
    unittest.main()
