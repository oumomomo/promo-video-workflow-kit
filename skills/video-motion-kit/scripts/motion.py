#!/usr/bin/env python3
"""Read-only distributable motion recipes and code; never opens a production DB."""
import argparse
import collections
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'references/catalog.json'
PROVENANCE = ROOT / 'references/provenance.json'
ALIASES = {
    '运镜': ['camera', '推近', '环绕', '推拉'], '数字': ['data', 'digit', 'counter', '计数'],
    '标题': ['typography', 'title', '文字'], '转场': ['transition', 'wipe', '切换'],
    '鼠标': ['cursor', 'interaction'], '滚动': ['scroll', 'rhythm'],
    '粒子': ['particle', 'effects'], '卡片': ['card', 'ui-entrance'],
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def local(name):
    if not isinstance(name, str) or Path(name).is_absolute():
        raise ValueError('分发目录只接受相对路径')
    path = (ROOT / name).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('来源路径越界')
    return path


def entries():
    data = read(CATALOG)
    if data.get('schemaVersion') != 1:
        raise ValueError('不支持的目录格式')
    return data['entries']


def find(key):
    matches = [e for e in entries() if e['id'] == key]
    if len(matches) != 1:
        raise ValueError('找不到唯一动效ID，请先search：' + key)
    return matches[0]


def source_files(entry):
    p = read(PROVENANCE)
    requested = sorted(set([entry['recipe'], *entry['files']]))
    provider = entry['provider']
    license_path = 'vendor/' + ('video-shotcraft' if provider == 'video-shotcraft' else 'motionvault') + '/LICENSE'
    requested.append(license_path)
    if provider == 'MotionVault':
        requested += ['vendor/motionvault/src/index.css', 'vendor/motionvault/tailwind.config.js']
    lookup = {f['path']: f for f in p['files']}
    checked = []
    for name in sorted(set(requested)):
        path = local(name)
        item = lookup.get(name)
        if not item or not path.is_file() or sha(path) != item['sha256']:
            raise ValueError('配方或源码缺失／内容变更：' + name)
        checked.append(item)
    return checked


def compact(e):
    return {k: e[k] for k in ('id', 'card', 'style_key', 'style_label', 'summary', 'category',
                              'provider', 'runtime', 'readiness', 'missingMedia')}


def search(args):
    terms = re.findall(r'[a-z0-9_-]+|[\u3400-\u9fff]+', args.query.lower())
    groups = []
    for term in terms:
        expanded = [term]
        for name, aliases in ALIASES.items():
            if name in term:
                expanded.extend(aliases)
        groups.append(expanded)
    results = []
    for e in entries():
        if args.runtime and e['runtime'] != args.runtime:
            continue
        if args.provider and e['provider'] != args.provider:
            continue
        if args.no_media and e['missingMedia']:
            continue
        haystack = ' '.join(str(e.get(k, '')) for k in ('id', 'style_label', 'summary', 'use', 'intention', 'category', 'category_zh', 'tags')).lower()
        matched = [any(t in haystack for t in group) for group in groups]
        score = sum(matched)
        # OR-ranked discovery; callers see matched terms, not a semantic score.
        if not groups or score:
            results.append((score, e))
    results.sort(key=lambda item: (-item[0], item[1]['id']))
    return {'source': 'read_only_distribution_catalog', 'matching': 'literal_terms_plus_small_alias_map_OR_ranked',
            'total': len(results), 'results': [{**compact(e), 'matchedTermGroups': score} for score, e in results[:args.limit]],
            'productionDatabaseReadOrWritten': False}


def resolve(args):
    e = find(args.id)
    checked = source_files(e)
    return {'entry': e, 'recipeText': local(e['recipe']).read_text(encoding='utf-8'),
            'sourceFiles': checked, 'catalogSha256': sha(CATALOG), 'previewIncluded': False,
            'next': 'Read the exact demo source, adapt to this shot; media gaps must be filled by user/new assets, not old bundled media.'}


def destination(value):
    root = Path(value).expanduser().resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError('输出目录必须为空，拒绝覆盖')
    return root


def export_entry(entry, out):
    checked = source_files(entry)
    out.mkdir(parents=True, exist_ok=True)
    for item in checked:
        target = out / item['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(local(item['path']), target)
    receipt = {'schemaVersion': 1, 'entry': entry, 'catalogSha256': sha(CATALOG),
               'files': checked, 'source': read(PROVENANCE)['providers'][entry['provider']],
               'existingMediaIncluded': False, 'userApproved': False,
               'meaning': 'source_export_not_a_finished_or_verified_shot'}
    write(out / 'MOTION-SOURCE.json', receipt)
    return receipt


def export(args):
    e = find(args.id)
    out = destination(args.out)
    receipt = export_entry(e, out)
    return {'state': 'source_exported', 'out': str(out), 'files': len(receipt['files']),
            'runtime': e['runtime'], 'missingMedia': e['missingMedia'], 'mediaIncluded': False}


def select_demo(entry, chosen):
    demos = entry['demos']
    if chosen:
        matches = [p for p in demos if p == chosen or Path(p).name == chosen]
        if len(matches) != 1:
            raise ValueError('--demo须指向此条目列出的唯一源码文件：' + ', '.join(demos))
        return matches[0]
    if len(demos) != 1:
        raise ValueError('此条目有多个实现，请先resolve并用--demo选择准确源码：' + ', '.join(demos))
    return demos[0]


def scaffold(args):
    e = find(args.id)
    if e['runtime'] != 'remotion':
        raise ValueError('这是网页交互源码；先export并把交互、滚动、时钟动画改为帧驱动，不能直接冒充Remotion镜头')
    if e['missingMedia']:
        raise ValueError('本包不含旧媒体／布局数据，请先export并替换为本次素材：' + ', '.join(e['missingMedia']))
    demo = select_demo(e, args.demo)
    text = local(demo).read_text(encoding='utf-8')
    exported = re.findall(r'export\s+(?:const|function|class)\s+([A-Za-z_$][\w$]*)', text)
    component = args.component
    if not component:
        name = Path(demo).stem
        if name in exported:
            component = name
        elif len(exported) == 1:
            component = exported[0]
        else:
            raise ValueError('请用--component明确导出组件：' + ', '.join(exported))
    if component not in exported or not re.fullmatch(r'[A-Za-z_$][\w$]*', component):
        raise ValueError('组件不在所选源码导出中')
    out = destination(args.out)
    receipt = export_entry(e, out / 'motion-source')
    (out / 'src').mkdir()
    (out / 'public').mkdir()
    # Pinned, external dependencies. No node_modules or downloaded browser included.
    dependencies = {'remotion': '4.0.513', '@remotion/cli': '4.0.513', 'react': '19.2.3', 'react-dom': '19.2.3'}
    if '@remotion/motion-blur' in e['npmImports']:
        dependencies['@remotion/motion-blur'] = '4.0.513'
    write(out / 'package.json', {'name': 'motion-shot-project', 'private': True, 'version': '0.0.0',
          'scripts': {'studio': 'remotion studio src/index.ts',
                      'still': 'remotion still src/index.ts MotionPreview out/frame.png',
                      'render': 'remotion render src/index.ts MotionPreview out/motion-candidate.mp4 --concurrency=2'},
          'dependencies': dependencies,
          'devDependencies': {'typescript': '5.9.3', '@types/react': '19.2.3', '@types/react-dom': '19.2.3'}})
    write(out / 'tsconfig.json', {'compilerOptions': {'target': 'ES2020', 'lib': ['ES2020', 'DOM'],
          'module': 'ESNext', 'moduleResolution': 'Bundler', 'jsx': 'react-jsx', 'esModuleInterop': True,
          'skipLibCheck': True, 'noEmit': True}, 'include': ['src', 'motion-source']})
    import_path = '../motion-source/' + str(Path(demo).with_suffix(''))
    (out / 'src/Root.tsx').write_text(
        "import React from 'react';\nimport {Composition} from 'remotion';\n" +
        f"import {{{component}}} from {json.dumps(import_path)};\n" +
        f'export const Root = () => <Composition id="MotionPreview" component={{{component}}} durationInFrames={{{args.frames}}} fps={{30}} width={{1920}} height={{1080}} />;\n', encoding='utf-8')
    (out / 'src/index.ts').write_text("import {registerRoot} from 'remotion';\nimport {Root} from './Root';\nregisterRoot(Root);\n", encoding='utf-8')
    write(out / 'workflow/motion-selection.json', {'schemaVersion': 1, 'selectedId': e['id'],
          'mode': 'reuse_source_candidate', 'sourceVersion': e['sourceVersion'], 'catalogSha256': sha(CATALOG),
          'recipeSha256': e['sourceSha256'], 'demo': demo, 'component': component,
          'scope': 'single_motion_demonstration_not_real_product_evidence', 'userApproved': False,
          'next': 'Adapt example objects, copy and styling to this project; inspect real frames and motion before adoption.'})
    return {'state': 'remotion_project_scaffolded', 'project': str(out), 'component': component,
            'sourceFiles': len(receipt['files']), 'mediaIncluded': False, 'dependenciesInstalled': False,
            'next': 'npm install, then npm run still / npm run render. Node/npm/browser runtime not bundled; output must be reviewed.'}


def record(args):
    e = find(args.id) if args.mode != 'invent' else None
    if not args.reason.strip():
        raise ValueError('须写清本次镜头选择理由')
    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        raise ValueError('制作项目不存在')
    workflow = (root / 'workflow').resolve()
    if not workflow.is_relative_to(root):
        raise ValueError('项目账本目录越界')
    path = workflow / 'motion-selection.json'
    if path.exists() and not path.resolve().is_relative_to(root):
        raise ValueError('项目账本文件越界')
    previous = read(path) if path.exists() else {'schemaVersion': 1, 'selections': []}
    if 'selections' not in previous:
        previous = {'schemaVersion': 1, 'scaffoldSelection': previous, 'selections': []}
    item = {'shot': args.shot, 'mode': args.mode, 'id': args.id, 'reason': args.reason,
            'change': args.change, 'avoid': args.avoid, 'catalogSha256': sha(CATALOG),
            'sourceVersion': e['sourceVersion'] if e else None, 'userApproved': False}
    if e:
        source_files(e)
    previous['selections'].append(item)
    write(path, previous)
    return {'state': 'project_selection_recorded', 'file': str(path), 'productionDatabaseWritten': False}


def audit(args):
    catalog = entries()
    provenance = read(PROVENANCE)
    errors = []
    ids = [e['id'] for e in catalog]
    if len(ids) != len(set(ids)):
        errors.append('重复ID')
    allowed = {f['path'] for f in provenance['files']}
    for f in provenance['files']:
        path = local(f['path'])
        if not path.is_file() or sha(path) != f['sha256']:
            errors.append('文件缺失或哈希变更：' + f['path'])
    media = {'.mp4', '.mov', '.webm', '.png', '.jpg', '.jpeg', '.gif', '.wav', '.mp3', '.woff', '.woff2', '.ttf', '.otf', '.sqlite', '.db'}
    for p in (ROOT / 'vendor').rglob('*'):
        if p.is_symlink():
            errors.append('禁止符号链接：' + str(p.relative_to(ROOT)))
        if p.is_file() and (p.suffix.lower() in media or str(p.relative_to(ROOT)) not in allowed):
            errors.append('非白名单／媒体文件：' + str(p.relative_to(ROOT)))
    for e in catalog:
        try:
            source_files(e)
        except ValueError as exc:
            errors.append(str(exc))
    result = {'state': 'audit_pass' if not errors else 'audit_fail', 'errors': errors,
              'entries': len(catalog), 'sourceFiles': len(provenance['files']), 'mediaFiles': 0 if not errors else 'see_errors',
              'entriesNeedingNewMedia': sum(bool(e['missingMedia']) for e in catalog),
              'meaning': 'file_integrity_and_manifest_check_not_all_components_rendered_or_aesthetically_approved'}
    if errors:
        raise ValueError(json.dumps(result, ensure_ascii=False))
    return result


def stats(args):
    data = entries()
    return {'entries': len(data), 'byProvider': dict(collections.Counter(e['provider'] for e in data)),
            'byRuntime': dict(collections.Counter(e['runtime'] for e in data)),
            'byCategory': dict(collections.Counter(e['category'] for e in data)),
            'entriesNeedingNewMedia': sum(bool(e['missingMedia']) for e in data),
            'previewsIncluded': False, 'editableProductionLibrary': False}


def main():
    p = argparse.ArgumentParser(description='只读动效分发目录：搜索配方、核对源码、导出、建Remotion单镜工程；不带旧媒体。')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('stats'); sub.add_parser('audit')
    s = sub.add_parser('search'); s.add_argument('query'); s.add_argument('--limit', type=int, choices=range(1, 101), default=8)
    s.add_argument('--runtime', choices=['remotion', 'web_react_interaction']); s.add_argument('--provider', choices=['MotionVault', 'video-shotcraft'])
    s.add_argument('--no-media', action='store_true')
    s = sub.add_parser('resolve'); s.add_argument('id')
    for name in ('export', 'scaffold'):
        s = sub.add_parser(name); s.add_argument('id'); s.add_argument('--out', required=True)
        if name == 'scaffold':
            s.add_argument('--demo'); s.add_argument('--component'); s.add_argument('--frames', type=int, choices=range(1, 1801), default=150)
    s = sub.add_parser('record'); s.add_argument('id'); s.add_argument('--project', required=True); s.add_argument('--shot', required=True)
    s.add_argument('--mode', choices=['reuse', 'remix', 'invent'], required=True); s.add_argument('--reason', required=True)
    s.add_argument('--change', default=''); s.add_argument('--avoid', default='')
    args = p.parse_args()
    try:
        result = {'stats': stats, 'audit': audit, 'search': search, 'resolve': resolve,
                  'export': export, 'scaffold': scaffold, 'record': record}[args.command](args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, FileNotFoundError, TypeError) as exc:
        print(json.dumps({'state': 'error', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
