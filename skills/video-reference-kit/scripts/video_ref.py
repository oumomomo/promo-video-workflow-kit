#!/usr/bin/env python3
"""Portable reference evidence and adoption, using the existing asset protocol."""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'backend/scripts/asset-library.py'
ENGINE = ROOT / 'vendor/video-shots/scripts/video-shots.mjs'
VERSION = '0.1.0-draft'
PRODUCER = 'video-reference-kit'


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    fd, name = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(body)
        os.replace(name, path)
    finally:
        if Path(name).exists():
            Path(name).unlink()


def run(command, *, cwd=None, data=None, timeout=180):
    result = subprocess.run([str(x) for x in command], cwd=cwd, input=data,
                            capture_output=True, text=True, encoding='utf-8', timeout=timeout)
    if result.returncode:
        raise ValueError((result.stderr or result.stdout)[-2500:].strip() or '执行失败')
    return result.stdout


def config_path():
    return Path(os.environ.get('OMM_ASSET_CONFIG', Path.home() / '.config/omm-asset-library/config.json')).expanduser().resolve()


def shared_configuration():
    path = config_path()
    if not path.is_file():
        return None
    value = load(path)
    if value.get('mode') == 'portable-reference-kit':
        raise ValueError('便携库请通过 --library 指定，不将其冒充统一库配置')
    if not value.get('db') or not value.get('cli'):
        raise ValueError('已有统一库配置无效；请修复配置，不创建替代库')
    return path, value


def protected_workspace(path):
    path = Path(path).resolve()
    for parent in [path, *path.parents]:
        if (parent / 'creator-workbench/src/asset-library/WORKFLOW.md').is_file():
            return True
    return False


class Library:
    def __init__(self, directory=None):
        shared = shared_configuration()
        if shared:
            if directory:
                raise ValueError('已配置统一素材库；不另建或切换便携库，请省略 --library')
            cfg, value = shared
            self.shared = True
            self.db = Path(value['db']).expanduser().resolve()
            self.entry = cfg.parent / 'entry.py'
            if not self.entry.is_file() or not self.db.is_file():
                raise ValueError('已有统一入口或数据库不可用；修复原配置，不自动降级')
            self.root = None
            self.command = [sys.executable, self.entry]
            self.read_only = bool(value.get('readOnly'))
        else:
            if not directory:
                raise ValueError('尚未接入统一库；先用 init --library 创建自己的资料库')
            if protected_workspace(Path.cwd()) or protected_workspace(directory):
                raise ValueError('当前工作区要求现有统一库；不能在此建立替代资料库')
            self.root = Path(directory).expanduser().resolve()
            cfg = load(self.root / 'config.json')
            if cfg.get('mode') != 'portable-reference-kit':
                raise ValueError('不是本工具初始化的便携资料库')
            self.shared = False
            self.db = (self.root / cfg['db']).resolve()
            if not self.db.is_relative_to(self.root) or not self.db.is_file():
                raise ValueError('资料库路径无效；不会自动创建替代数据库')
            self.command = [sys.executable, BACKEND, '--db', self.db]
            self.read_only = False

    def call(self, *args, request=None):
        reads = {'get', 'lookup', 'search', 'read-result', 'usage', 'stats'}
        if self.read_only and args[0] not in reads:
            raise ValueError('统一库当前是只读配置')
        raw = run([*self.command, *args], data=encoded(request) if request is not None else None)
        result = json.loads(raw)
        if isinstance(result, dict) and result.get('state') == 'pending_retry':
            raise ValueError('提交未完成，结果已保留在原入口待办中')
        return result


def init_library(args):
    if shared_configuration() or protected_workspace(Path.cwd()) or protected_workspace(args.library):
        raise ValueError('已有统一素材入口或工作区约束；请继续使用原主库')
    root = Path(args.library).expanduser().resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError('目录非空，拒绝覆盖')
    root.mkdir(parents=True, exist_ok=True)
    run([sys.executable, BACKEND, '--db', root / 'assets.sqlite', 'init'])
    run([sys.executable, BACKEND, '--db', root / 'assets.sqlite', 'init-results'])
    write(root / 'config.json', {'schemaVersion': 1, 'mode': 'portable-reference-kit', 'db': 'assets.sqlite'})
    return {'state': 'initialized', 'library': str(root), 'mediaIncluded': False}


def doctor(args):
    binaries = {n: shutil.which(n) for n in ('node', 'ffmpeg', 'ffprobe')}
    node = run([binaries['node'], '--version']).strip() if binaries['node'] else None
    available = all(binaries.values()) and bool(node and int(node.lstrip('v').split('.')[0]) >= 18)
    return {'ok': bool(available and sys.version_info >= (3, 10)), 'python': sys.version.split()[0],
            'node': node, 'binaries': binaries, 'sharedConfigPresent': config_path().is_file(),
            'scope': '检查本地依赖，不调用云端，也不检查成片质量'}


def probe(path):
    result = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path]))
    if not any(x.get('codec_type') == 'video' for x in result.get('streams', [])):
        raise ValueError('输入没有视频流')
    duration = float(result['format']['duration'])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('无法核对视频时长')
    return result, duration


def submit(lib, rid, stream, documents):
    current = lib.call('get', rid)
    head = next((x for x in current.get('resultHeads', [])
                 if x['producer'] == PRODUCER and x['stream'] == stream), None)
    request = {'schemaVersion': 1, 'producer': PRODUCER, 'stream': stream,
               'asset': {'id': rid}, 'documents': documents}
    # Same-content retries carry the same parent and request identity.
    if head:
        old = lib.call('read-result', rid, '--producer', PRODUCER, '--stream', stream)
        bodies = [(d['key'], d['body'], d.get('format', '.md')) for d in old['payload']['documents']]
        if bodies == [(d['key'], d['body'], d.get('format', '.md')) for d in documents]:
            return {'state': 'committed', 'assetId': rid, 'version': head['version'], 'replayed': True}
        request['baseVersion'] = head['version']
    request['requestId'] = PRODUCER + ':' + hashlib.sha256(encoded(request).encode()).hexdigest()
    return lib.call('submit', '--request', '-', request=request)


def prepare(args, lib):
    if not (math.isfinite(args.threshold) and 0 < args.threshold < 1 and
            math.isfinite(args.max_seconds) and args.max_seconds > 0 and args.max_shots > 0):
        raise ValueError('阈值需在0到1之间，时长和镜头上限需为正数')
    source = Path(args.source).expanduser().resolve()
    if not source.is_file():
        raise ValueError('本地原件不存在')
    sha = digest(source)
    prior = lib.call('lookup', '--file', str(source))
    if prior.get('match') == 'excluded':
        raise ValueError('此原件已被统一入口排除')
    cached = next((r for r in prior.get('records', []) if r['kind'] == 'reference_video' and
                   any(h['producer'] == PRODUCER and h['stream'] == 'mechanical-evidence'
                       for h in r.get('resultHeads', []))), None)
    if cached:
        evidence = mechanical(lib, cached['id'])
        if evidence['manifest'].get('toolVersion') != VERSION:
            raise ValueError('已有证据来自不同工具版本；先检查旧结果，不自动覆盖或重拆')
        target = Path(evidence['evidenceDirectory'])
        verify_evidence(target, evidence['manifest'])
        rid = register_evidence(args, lib, target, evidence['manifest'])
        return {'state': 'reused', 'assetId': rid, 'sourceSha256': sha, 'evidence': str(target),
                'requestedOutUsed': False, 'semanticReview': '保留已有笔记，按本次用途检查缺项'}
    if args.out:
        target = Path(args.out).expanduser().resolve()
    elif lib.root:
        target = lib.root / 'references' / sha
    else:
        raise ValueError('统一库模式请用 --out 指定本项目的持久参考目录')
    if target.exists():
        manifest = load(target / 'manifest.json')
        if manifest.get('sourceSha256') != sha or manifest.get('toolVersion') != VERSION:
            raise ValueError('原件或工具版本不同；使用新的输出目录，保留原分析')
        verify_evidence(target, manifest)
        rid = register_evidence(args, lib, target, manifest)
        return {'state': 'reused', 'assetId': rid, 'sourceSha256': sha, 'evidence': str(target),
                'semanticReview': '见版本化笔记；机械证据不等于已精拉'}
    metadata, duration = probe(source)
    if duration > args.max_seconds:
        raise ValueError('超过本次时长上限；可明确提高 --max-seconds，或提供已记录偏移的裁段')
    target.parent.mkdir(parents=True, exist_ok=True)
    lock = target.parent / ('.' + target.name + '.lock')
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError('同一输出正在准备或遗留锁待检查；不会重复启动')
    stage = target.parent / ('.' + target.name + '.' + uuid.uuid4().hex + '.partial')
    try:
        stage.mkdir()
        suffix = source.suffix.lower()
        if not re.fullmatch(r'\.[a-z0-9]{1,8}', suffix):
            suffix = '.video'
        local = stage / ('source' + suffix)
        shutil.copy2(source, local)
        if digest(local) != sha or digest(source) != sha:
            raise ValueError('原件复制期间发生变化，停止登记')
        raw = run(['node', ENGINE, 'seed', local.name, '--threshold', args.threshold,
                   '--min', '0', '--track', 'track.json', '--title', args.title, '--lang', 'zh'], cwd=stage)
        shots = json.loads(raw)
        if len(shots.get('shots', [])) > args.max_shots:
            raise ValueError('切镜候选超过本次上限；核对阈值或明确提高 --max-shots')
        write(stage / 'shots.json', shots)
        run(['node', ENGINE, 'frames', 'shots.json', '--video', local.name], cwd=stage)
        for shot in shots['shots']:
            for side in ('a', 'b'):
                frame = stage / 'frames' / (shot['id'] + side + '.jpg')
                if not frame.is_file() or frame.stat().st_size == 0:
                    raise ValueError('关键帧提取不完整，保留部分结果但不登记完成')
        write(stage / 'probe.json', metadata)
        manifest = {'schemaVersion': 1, 'toolVersion': VERSION, 'sourceSha256': sha,
                    'localSource': local.name, 'durationSeconds': duration, 'title': args.title,
                    'semanticStatus': 'pending_review', 'audioStatus': 'not_listened' if shots['meta']['hasAudio'] else 'no_audio_stream',
                    'detector': {'threshold': args.threshold, 'minShotSeconds': 0, 'boundaries': 'machine_candidates'},
                    'files': {}}
        for file in sorted(stage.rglob('*')):
            if file.is_file():
                manifest['files'][str(file.relative_to(stage))] = digest(file)
        write(stage / 'manifest.json', manifest)
        if target.exists():
            raise ValueError('目标目录已出现，拒绝覆盖')
        stage.rename(target)
    finally:
        lock.rmdir()
    rid = register_evidence(args, lib, target, manifest)
    return {'state': 'prepared', 'assetId': rid, 'sourceSha256': sha, 'evidence': str(target),
            'candidateShots': len(shots['shots']), 'semanticReview': 'pending', 'cloudCalls': 0}


def verify_evidence(directory, manifest):
    directory = Path(directory).resolve()
    for rel, expected in manifest['files'].items():
        file = (directory / rel).resolve()
        if not file.is_relative_to(directory) or not file.is_file() or digest(file) != expected:
            raise ValueError('证据文件缺失、越界或哈希不匹配：' + rel)
    local = (directory / manifest['localSource']).resolve()
    if not local.is_relative_to(directory) or digest(local) != manifest['sourceSha256']:
        raise ValueError('保存原件与登记身份不一致')


def register_evidence(args, lib, target, manifest):
    prior = lib.call('lookup', '--file', str(target / manifest['localSource']))
    if prior.get('match') == 'excluded':
        raise ValueError('此原件已被统一入口排除')
    existing = next((r for r in prior.get('records', []) if r['kind'] == 'reference_video'), None)
    arguments = ['register', '--file', str(target / manifest['localSource']), '--kind', 'reference_video']
    if not existing:
        arguments += ['--title', args.title, '--category', '视频表达参考']
    # Existing product provenance, categories, titles and review state are preserved.
    item = lib.call(*arguments)
    old = None
    if any(h['producer'] == PRODUCER and h['stream'] == 'mechanical-evidence' for h in item.get('resultHeads', [])):
        old = mechanical(lib, item['id'])
    description = {'schemaVersion': 1, 'sourceSha256': manifest['sourceSha256'], 'evidenceDirectory': str(target),
                   'manifest': manifest, 'rightsDeclaration': args.rights or (old or {}).get('rightsDeclaration', 'unknown'),
                   'rightsEvidence': args.rights_evidence if args.rights_evidence is not None else (old or {}).get('rightsEvidence', ''),
                   'note': '权利为提交者声明，未被工具核验；此条不自动成为产品UI真源或已复核分析'}
    submit(lib, item['id'], 'mechanical-evidence', [
        {'key': 'mechanical-evidence', 'body': encoded(description), 'format': '.json'}])
    return item['id']


def mechanical(lib, rid):
    result = lib.call('read-result', rid, '--producer', PRODUCER, '--stream', 'mechanical-evidence')
    return json.loads(result['payload']['documents'][0]['body'])


def validate_notes(notes, evidence):
    if notes.get('sourceSha256') != evidence['sourceSha256']:
        raise ValueError('笔记必须绑定相同原片哈希')
    inspection = notes.get('inspection', {})
    if inspection.get('method') not in ('agent_visual_review', 'human_review') or not str(inspection.get('scope', '')).strip():
        raise ValueError('请填写实际观察方式和范围，不把机器底稿当作已复核')
    if not str(notes.get('summary', '')).strip() or not isinstance(notes.get('phases'), list) or not notes['phases']:
        raise ValueError('需填写用途摘要和至少一个实际观察片段')
    duration = evidence['manifest']['durationSeconds']
    for phase in notes['phases']:
        start, end = phase.get('start'), phase.get('end')
        if isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            raise ValueError('片段时间必须为数字')
        if not (math.isfinite(start) and math.isfinite(end) and 0 <= start < end <= duration):
            raise ValueError('片段时间无效或超出原片')
        if not all(isinstance(phase.get(k), str) and phase[k].strip() for k in ('observed', 'inherit', 'change', 'avoid')):
            raise ValueError('每段需写明观察、继承、改变与排除项')


def notes_command(args, lib):
    evidence = mechanical(lib, args.id)
    directory = Path(evidence['evidenceDirectory'])
    verify_evidence(directory, evidence['manifest'])
    if args.action == 'template':
        out = Path(args.out).resolve()
        if out.exists():
            raise ValueError('笔记目标已存在，拒绝覆盖')
        value = {'schemaVersion': 1, 'sourceSha256': evidence['sourceSha256'], 'summary': '',
                 'inspection': {'method': 'unreviewed', 'scope': '', 'observer': '', 'date': ''},
                 'audio': {'status': evidence['manifest']['audioStatus'], 'observations': ''},
                 'phases': [{'start': 0, 'end': evidence['manifest']['durationSeconds'],
                             'observed': '', 'inherit': '', 'change': '', 'avoid': ''}]}
        write(out, value)
        return {'state': 'template_created', 'file': str(out), 'reviewStatus': 'pending'}
    value = load(args.file)
    validate_notes(value, evidence)
    return submit(lib, args.id, 'semantic-notes', [{'key': 'semantic-notes', 'body': encoded(value), 'format': '.json'}])


def bind(args, lib):
    if not (math.isfinite(args.start) and math.isfinite(args.end) and 0 <= args.start < args.end):
        raise ValueError('引用区间必须是有效的起止时间')
    if not all(str(v).strip() for v in (args.shot, args.inherit, args.change, args.avoid)):
        raise ValueError('镜头ID、继承、改变和排除项不能为空')
    evidence = mechanical(lib, args.id)
    verify_evidence(evidence['evidenceDirectory'], evidence['manifest'])
    reviewed = lib.call('read-result', args.id, '--producer', PRODUCER, '--stream', 'semantic-notes')
    notes = json.loads(reviewed['payload']['documents'][0]['body'])
    validate_notes(notes, evidence)
    covered = any(p['start'] <= args.start < args.end <= p['end'] for p in notes['phases'])
    if not covered:
        raise ValueError('引用区间不在已记录的观察片段内')
    if args.use == 'media' and (evidence['rightsDeclaration'] not in ('owned', 'licensed') or not evidence.get('rightsEvidence')):
        raise ValueError('直接采用原片画面需权利声明和依据；表达借鉴可用 --use reference')
    project = Path(args.project).resolve()
    if not project.is_dir():
        raise ValueError('请先指定存在的制作项目目录')
    path = project / 'workflow/reference-uses.json'
    if not path.resolve().is_relative_to(project):
        raise ValueError('项目引用目标通过符号链接指向项目之外，拒绝写入')
    ledger = load(path) if path.exists() else {'schemaVersion': 1, 'references': []}
    if ledger.get('schemaVersion') != 1 or not isinstance(ledger.get('references'), list):
        raise ValueError('现有项目引用格式不同，不能覆盖')
    record = {'shotId': args.shot, 'assetId': args.id, 'sourceSha256': evidence['sourceSha256'],
              'analysisVersion': reviewed['version'], 'start': args.start, 'end': args.end,
              'use': args.use, 'inherit': args.inherit, 'change': args.change, 'avoid': args.avoid,
              'status': 'planned', 'productCapabilityVerified': False, 'userApproval': None}
    old = next((r for r in ledger['references'] if r['shotId'] == args.shot), None)
    if old and old != record:
        raise ValueError('此镜头已有不同引用；本版不覆盖，另用新镜头ID或先人工核对修订')
    if not old:
        ledger['references'].append(record)
    project_id = 'local-project:' + hashlib.sha256(str(project).encode()).hexdigest()[:24]
    receipt = lib.call('submit-usage', '--request', '-', request={
        'projectId': project_id, 'scope': 'video-reference-kit', 'ledger': ledger})
    write(path, ledger)
    return {'state': 'bound', 'projectFile': str(path), 'adoptionReceipt': receipt,
            'shotId': args.shot, 'status': 'planned', 'userApproved': False}


def export(args, lib):
    item = lib.call('get', args.id)
    values = []
    for head in item.get('resultHeads', []):
        if head['producer'] == PRODUCER:
            result = lib.call('read-result', args.id, '--producer', PRODUCER, '--stream', head['stream'])
            values.append({'stream': head['stream'], 'version': head['version'], 'documents': result['payload']['documents']})
    out = Path(args.out).resolve()
    if out.exists():
        raise ValueError('导出目标已存在，拒绝覆盖')
    write(out, {'schemaVersion': 1, 'assetId': item['id'], 'title': item['title'], 'sources': item['sources'],
                'results': values, 'mediaIncluded': False, 'publicDistributionReviewed': False})
    return {'state': 'exported', 'file': str(out), 'scope': '个人项目导出，含原记录正文与本地定位；未做公开脱敏'}


def parser():
    p = argparse.ArgumentParser(description='参考视频：基础证据、统一登记、检索与镜头采用')
    p.add_argument('--library', help='未配置统一库的使用者，显式指定自己的便携库目录')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    i = sub.add_parser('init'); i.add_argument('--library', required=True)
    a = sub.add_parser('prepare'); a.add_argument('--source', required=True); a.add_argument('--title', required=True)
    a.add_argument('--out'); a.add_argument('--threshold', type=float, default=.3)
    a.add_argument('--max-seconds', type=float, default=180); a.add_argument('--max-shots', type=int, default=80)
    a.add_argument('--rights', choices=['unknown', 'owned', 'licensed']); a.add_argument('--rights-evidence')
    s = sub.add_parser('search'); s.add_argument('query', nargs='?', default='')
    g = sub.add_parser('get'); g.add_argument('id')
    n = sub.add_parser('notes'); ns = n.add_subparsers(dest='action', required=True)
    for action in ('template', 'submit'):
        q = ns.add_parser(action); q.add_argument('--id', required=True)
        q.add_argument('--out' if action == 'template' else '--file', required=True)
    b = sub.add_parser('bind')
    for name in ('project', 'shot', 'id', 'inherit', 'change', 'avoid'): b.add_argument('--' + name, required=True)
    b.add_argument('--start', type=float, required=True); b.add_argument('--end', type=float, required=True)
    b.add_argument('--use', choices=['reference', 'media'], default='reference')
    e = sub.add_parser('export'); e.add_argument('--id', required=True); e.add_argument('--out', required=True)
    return p


def main():
    args = parser().parse_args()
    try:
        if args.command == 'doctor':
            value = doctor(args)
        elif args.command == 'init':
            value = init_library(args)
        else:
            lib = Library(args.library)
            if lib.read_only and (args.command in ('prepare', 'bind') or
                                  (args.command == 'notes' and args.action == 'submit')):
                raise ValueError('统一库当前是只读配置，拒绝本次写入')
            commands = {'prepare': prepare, 'notes': notes_command, 'bind': bind, 'export': export}
            if args.command in commands:
                value = commands[args.command](args, lib)
            elif args.command == 'search':
                value = lib.call('search', args.query, '--kind', 'reference_video')
            else:
                value = lib.call('get', args.id)
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 1 if value.get('ok') is False else 0
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({'state': 'failed', 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
