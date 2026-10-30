#!/usr/bin/env python3
"""Build only reviewed source paths; never sweep a media or runtime directory."""
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/video-reference-kit'
BACKEND_MODULES = ('asset-library', 'asset_classification', 'asset_compat', 'asset_exclusion',
                   'asset_results', 'asset_summaries', 'asset_usage', 'asset_workflow_catalog',
                   'asset_audio_results', 'asset_motion_results')


def files():
    chosen = [ROOT / n for n in ('.gitignore', 'README.md', 'LICENSE', 'RELEASE-STATUS.md',
                                 'THIRD_PARTY_NOTICES.md', 'video_ref.py', 'video_make.py', 'video_motion.py', 'video_review.py', 'video_library.py', 'video_tools.py', 'video_setup.py',
                                 'tests/test_reference_flow.py', 'tests/test_production_flow.py', 'tests/test_motion_flow.py', 'tests/test_library_flow.py', 'tests/test_production_tools.py', 'tests/test_google_music.py', 'tests/test_first_install.py', 'scripts/package.py')]
    for folder in ('docs', 'templates', 'examples'):
        chosen += sorted((ROOT / folder).glob('*.md'))
    chosen += [SKILL / 'SKILL.md', SKILL / 'scripts/video_ref.py', SKILL / 'references/commands.md']
    chosen += [SKILL / 'backend/scripts' / (n + '.py') for n in BACKEND_MODULES]
    chosen += [SKILL / 'backend/src/asset-library' / n for n in ('exclusion.sql', 'historical-classification.json')]
    chosen += [SKILL / 'vendor/video-shots' / n for n in ('LICENSE', 'README.md', 'scripts/video-shots.mjs',
                                                        'scripts/report.js', 'scripts/report.css')]
    making = ROOT / 'skills/video-making-kit'
    chosen += [making / n for n in ('SKILL.md', 'scripts/video_make.py', 'references/commands.md', 'references/production.md', 'references/promo-pitfalls.md', 'references/environment-setup.md')]
    motion = ROOT / 'skills/video-motion-kit'
    subprocess.run([sys.executable, '-B', str(motion / 'scripts/motion.py'), 'audit'], check=True, capture_output=True)
    chosen += [motion / n for n in ('SKILL.md', 'scripts/motion.py', 'references/usage.md', 'references/catalog.json', 'references/provenance.json')]
    provenance = json.loads((motion / 'references/provenance.json').read_text())
    for item in provenance['files']:
        path = motion / item['path']
        if path.suffix.lower() not in ('', '.tsx', '.ts', '.md', '.css', '.js'):
            raise ValueError('动效包只接受审阅过的文本源码：' + item['path'])
        chosen.append(path)
    library = ROOT / 'skills/video-asset-library'
    chosen += [library / n for n in ('SKILL.md', 'scripts/library.py', 'references/library-workflow.md')]
    production = ROOT / 'skills/video-production-tools'
    for name in ('SKILL.md', 'SOURCE.json', 'requirements.txt',
                 'scripts/runtime.py', 'scripts/product_reference.py', 'scripts/check_shot_evidence.py',
                 'scripts/archive_state.py', 'scripts/ledger.py', 'scripts/music.py', 'scripts/music_google.py', 'scripts/contract.py',
                 'voice/scripts/voiceover_cli.py', 'voice/references/voice-style-registry.json',
                 'analysis/pipeline.py', 'analysis/precision.py', 'analysis/sound_reuse.py',
                 'analysis/render_report.py', 'analysis/render_evidence.py',
                 'references/operations.md', 'references/review-method.md', 'references/visual-contract.template.json'):
        chosen.append(production / name)
    review = ROOT / 'plugins/codex-video-review'
    for name in ('.codex-plugin/plugin.json', '.mcp.json', 'package.json', 'package-lock.json',
                 'README.md', 'SOURCE.json', 'DEPENDENCY-NOTICES.md', 'src/widget.js', 'dist/widget.js',
                 'mcp/server.mjs', 'mcp/render_review_frame.py', 'web/index.html', 'web/style.css',
                 'scripts/probe.mjs', 'scripts/portable-probe.mjs', 'scripts/preview.mjs', 'skills/video-review/SKILL.md'):
        chosen.append(review / name)
    for p in chosen:
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(ROOT):
            raise ValueError('白名单文件缺失或越界：' + str(p.relative_to(ROOT)))
    if json.loads((SKILL / 'backend/src/asset-library/historical-classification.json').read_text()) != {}:
        raise ValueError('发行包不得携带历史生产分类数据')
    return sorted(set(chosen))


def main():
    parser = argparse.ArgumentParser(description='生成本地候选源码包，不执行发布')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out).expanduser().resolve()
    if out.exists():
        raise ValueError('目标已存在，拒绝覆盖')
    sources = files()
    manifest = {'version': '0.7.3-local-candidate', 'status': 'github_test_preview_candidate',
                'licenseReview': 'maintainer_confirmed_MIT_with_third_party_exceptions', 'motionEntries': 363, 'existingMediaIncluded': False, 'productionToolsIncluded': True, 'promoPitfallRules': 24, 'cloudCredentialsIncluded': False, 'ownAssetLibraryEntryIncluded': True, 'reviewPluginIncluded': True, 'reviewNodeModulesIncluded': False, 'files': []}
    payloads = []
    for p in sources:
        data = p.read_bytes(); relative = str(p.relative_to(ROOT))
        manifest['files'].append({'path': relative, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        payloads.append((relative, data))
    payloads.append(('SOURCE-MANIFEST.json', (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()))
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for relative, data in payloads:
            info = zipfile.ZipInfo('video-workflow-kit-v0.7.3/' + relative, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    print(json.dumps({'state': 'packaged', 'files': len(sources), 'path': str(out),
                      'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
                      'publiclyReleased': False, 'licenseReview': 'maintainer_confirmed_MIT_with_third_party_exceptions'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
