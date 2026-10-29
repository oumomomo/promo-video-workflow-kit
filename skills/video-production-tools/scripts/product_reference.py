#!/usr/bin/env python3
"""Archive product media and publish reviewed, searchable segment cards.

The cards are attached to the existing asset-library record. This program
checks identity and structure; an agent/editor must actually inspect media.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


LIBRARY = Path(__file__).with_name('asset-library.py')
KINDS = {'.mp4': 'reference_video', '.mov': 'reference_video', '.webm': 'reference_video',
         '.mkv': 'reference_video', '.png': 'reference_image', '.jpg': 'reference_image',
         '.jpeg': 'reference_image', '.webp': 'reference_image'}
ROLES = {'product_ui_original', 'feedback_context', 'conversation_context', 'unverified'}


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def video_duration(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                             '-of', 'default=noprint_wrappers=1:nokey=1', str(path)],
                            text=True, capture_output=True)
    if result.returncode:
        raise ValueError('ffprobe 无法读取原片时长：' + result.stderr.strip())
    try:
        duration = float(result.stdout.strip())
    except ValueError as error:
        raise ValueError('原片时长无效') from error
    if duration <= 0:
        raise ValueError('原片时长无效')
    return duration


def library(db, *args):
    from runtime import gateway
    return gateway(*args)


def paths(project, digest, role, suffix):
    folder = {'product_ui_original': 'product-originals', 'unverified': 'pending-evidence',
              'feedback_context': 'context-evidence', 'conversation_context': 'context-evidence'}[role]
    base = project / 'handoff' / 'references' / folder / digest[:16]
    return base, base / ('source' + suffix)


def intake(args):
    source, project = args.file.resolve(), args.project.resolve()
    if not source.is_file() or source.suffix.lower() not in KINDS:
        raise ValueError('输入必须是现有 PNG/JPEG/WebP 图片或 MP4/MOV/WebM/MKV 视频')
    if args.role not in ROLES:
        raise ValueError('不支持的材料角色')
    if args.role == 'product_ui_original' and not all((x or '').strip() for x in
                                                   (args.product_name, args.provenance, args.inspection_scope)):
        raise ValueError('确认产品原片前，必须提供产品名、来源依据和已检查范围')
    if args.role != 'product_ui_original' and any((x or '').strip() for x in
                                                   (args.product_name, args.provenance, args.inspection_scope)):
        raise ValueError('产品身份字段只能随 product_ui_original 提交')
    digest = sha256(source)
    existing_reference_root = project / 'handoff' / 'references'
    if source.is_relative_to(existing_reference_root) and not (
            args.role == 'product_ui_original'
            and source.is_relative_to(existing_reference_root / 'pending-evidence')):
        # Existing project references are already durable; avoid a second media copy.
        base = project / 'workflow' / 'product-reference-cards' / digest[:16]
        target = source
    else:
        base, target = paths(project, digest, args.role, source.suffix.lower())
    base.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(source, target)
    if sha256(target) != digest:
        raise ValueError('持久副本 SHA-256 与上传文件不一致')
    source_info = {'schemaVersion': 1, 'assetId': 'asset:' + digest, 'sha256': digest,
                   'sourcePath': str(source), 'archivedPath': str(target), 'role': args.role,
                   'productName': args.product_name or '', 'sourceProvenance': args.provenance or '',
                   'inspectionScope': args.inspection_scope or '', 'originalFilename': source.name}
    if KINDS[source.suffix.lower()] == 'reference_video':
        source_info['durationSeconds'] = video_duration(target)
    manifest = base / 'source-index.json'
    if manifest.exists():
        old = json.loads(manifest.read_text())
        if old['sha256'] != digest:
            raise ValueError('归档目录已有不同哈希的原件')
        if old['role'] != args.role and not (old['role'] == 'unverified' and args.role == 'product_ui_original'):
            raise ValueError('已有材料角色不同；先核对旧记录，不在入库命令中静默改写角色')
    manifest.write_text(json.dumps(source_info, ensure_ascii=False, indent=2) + '\n')
    command = ['register', '--file', str(target), '--kind', KINDS[source.suffix.lower()],
               '--title', args.title or source.stem, '--evidence-role', args.role]
    if args.role == 'product_ui_original':
        command += ['--product-name', args.product_name, '--source-provenance', args.provenance,
                    '--inspection-scope', args.inspection_scope]
    record = library(args.db, *command)
    card_path = base / 'segments.json'
    if args.role in {'product_ui_original', 'unverified'} and not card_path.exists():
        card = {'schemaVersion': 1, 'assetId': record['id'], 'sourceSha256': digest,
                'mediaType': 'video' if KINDS[source.suffix.lower()] == 'reference_video' else 'image',
                'productName': args.product_name or '', 'segments': [],
                'reviewNote': '待实际观看／查看并按界面状态和动作拆分；自动切点只是候选'}
        card_path.write_text(json.dumps(card, ensure_ascii=False, indent=2) + '\n')
    return {'assetId': record['id'], 'role': args.role, 'archivedPath': str(target),
            'sha256Verified': True, 'segmentCards': str(card_path) if card_path.exists() else None,
            'next': '查看原件并填写片段卡，再运行 publish；空片段卡不会进入检索'}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_cards(card, source, record):
    if card.get('schemaVersion') != 1 or card.get('sourceSha256') != source['sha256']:
        raise ValueError('片段卡版本或原片 SHA-256 不匹配')
    if card.get('assetId') != record['id']:
        raise ValueError('片段卡资产 ID 不匹配')
    segments = card.get('segments')
    if not isinstance(segments, list) or not segments:
        raise ValueError('至少填写一个已观察片段；空模板不能发布')
    seen = set()
    for item in segments:
        ident = item.get('id')
        if not nonempty(ident) or ident in seen:
            raise ValueError('片段 ID 为空或重复')
        seen.add(ident)
        if item.get('status') not in {'candidate', 'structure_reviewed', 'action_reviewed'}:
            raise ValueError(f'{ident}: 无效状态')
        if not all(nonempty(item.get(field)) for field in ('title', 'observed', 'reviewScope')):
            raise ValueError(f'{ident}: 标题、实际观察和检查范围不能为空')
        if card['mediaType'] == 'video':
            start, end = item.get('startSeconds'), item.get('endSeconds')
            if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (start, end)) or not 0 <= start < end:
                raise ValueError(f'{ident}: 视频时间段无效')
            if end > source['durationSeconds'] + 0.05:
                raise ValueError(f'{ident}: 视频时间段超出原片时长')
            if item['status'] != 'candidate':
                frames = item.get('keyframesSeconds')
                if not isinstance(frames, list) or not frames or any(
                        not isinstance(t, (int, float)) or isinstance(t, bool) or not start <= t <= end
                        for t in frames):
                    raise ValueError(f'{ident}: 已核实视频片段须有范围内的关键帧时间')
                if item['reviewScope'] == 'sampled_frames':
                    sampled = item.get('sampledSeconds')
                    if not isinstance(sampled, list) or not sampled or any(
                            not isinstance(t, (int, float)) or isinstance(t, bool) or not start <= t <= end
                            for t in sampled):
                        raise ValueError(f'{ident}: 抽帧核实须列出实际查看秒数')
                elif item['reviewScope'] == 'continuous_reviewed':
                    reviewed = item.get('reviewedTimeRangeSeconds')
                    if not isinstance(reviewed, list) or len(reviewed) != 2 or not all(
                            isinstance(t, (int, float)) and not isinstance(t, bool) for t in reviewed
                    ) or reviewed[0] > start or reviewed[1] < end:
                        raise ValueError(f'{ident}: 连续核实须声明覆盖该段的审看范围')
                else:
                    raise ValueError(f'{ident}: 视频检查范围无效')
        elif not nonempty(item.get('imageRegion')):
            raise ValueError(f'{ident}: 图片必须定位画面区域')
        if item['status'] == 'action_reviewed':
            if card['mediaType'] != 'video' or item['reviewScope'] != 'continuous_reviewed':
                raise ValueError(f'{ident}: 动作核实必须连续审看原片')
            if not all(nonempty(item.get(field)) for field in ('action', 'beforeState', 'afterState')):
                raise ValueError(f'{ident}: 动作、前态和后态不能为空')
        if item['status'] == 'structure_reviewed' and item['reviewScope'] not in {
                'still_reviewed', 'sampled_frames', 'continuous_reviewed'}:
            raise ValueError(f'{ident}: 界面结构的检查范围无效')
        if item['status'] != 'action_reviewed' and item.get('actionClaim'):
            raise ValueError(f'{ident}: 未核实动作不得写 actionClaim')


def publish(args):
    card_path = args.cards.resolve()
    base = card_path.parent
    source_index = json.loads((base / 'source-index.json').read_text())
    archived = Path(source_index['archivedPath'])
    if not archived.is_file() or sha256(archived) != source_index['sha256']:
        raise ValueError('原件丢失或哈希已改变')
    if source_index['role'] != 'product_ui_original':
        raise ValueError('只有经核实的产品原片可发布产品片段卡；先确认身份再入库')
    record = library(args.db, 'get', source_index['assetId'], '--scope', 'product-ui')
    card = json.loads(card_path.read_text())
    validate_cards(card, source_index, record)
    # Publish only cards explicitly reviewed. Candidates remain in the local
    # project file so search cannot mistake them for verified product behavior.
    selected = [item for item in card['segments'] if item['status'] != 'candidate']
    if not selected:
        raise ValueError('没有已复核片段可发布')
    searchable = {key: card[key] for key in ('schemaVersion', 'assetId', 'sourceSha256', 'mediaType', 'productName')}
    searchable['segments'] = selected
    searchable['boundary'] = '界面结构核实不等于动作核实；只复用每段 observed 与 reviewScope 覆盖的内容'
    published = base / 'segments-reviewed.json'
    published.write_text(json.dumps(searchable, ensure_ascii=False, indent=2) + '\n')
    library(args.db, 'register', '--file', str(archived), '--kind', record['kind'],
            '--title', record['title'], '--evidence-role', 'product_ui_original',
            '--product-name', source_index['productName'],
            '--source-provenance', source_index['sourceProvenance'],
            '--inspection-scope', source_index['inspectionScope'], '--analysis', str(published))
    return {'assetId': record['id'], 'publishedSegments': len(selected),
            'candidateSegmentsHeldBack': len(card['segments']) - len(selected),
            'searchDocument': str(published), 'sourceSha256': source_index['sha256']}


def find(args):
    tokens = [part.lower() for part in args.query.split() if part]
    if not tokens:
        raise ValueError('请输入页面、组件或动作关键词')
    matches = []
    offset = 0
    while offset < 500:
        page = library(args.db, 'search', args.query, '--scope', 'product-ui',
                       '--limit', '100', '--offset', str(offset))
        for row in page['items']:
            record = library(args.db, 'get', row['id'], '--scope', 'product-ui')
            current = next((doc for doc in record['documents']
                            if str(doc['path']).endswith('/segments-reviewed.json')), None)
            if not current:
                continue
            cards = json.loads(current['body'])
            if cards.get('sourceSha256') not in {obj['sha'] for obj in record['objects']}:
                continue
            for item in cards.get('segments', []):
                if item.get('status') not in {'structure_reviewed', 'action_reviewed'}:
                    continue
                haystack = ' '.join(str(item.get(field) or '') for field in
                                    ('title', 'observed', 'action', 'keywords')).lower()
                haystack += ' ' + str(cards.get('productName') or '').lower()
                if not all(token in haystack for token in tokens):
                    continue
                matches.append({'assetId': record['id'], 'sourceSha256': cards['sourceSha256'],
                                'sourceLocations': [loc['path'] for obj in record['objects']
                                                    if obj['sha'] == cards['sourceSha256']
                                                    for loc in obj['locations']],
                                'segment': item})
        offset += len(page['items'])
        if offset >= page['count'] or not page['items']:
            break
    matches.sort(key=lambda item: (item['segment']['status'] != 'action_reviewed',
                                   item['assetId'], item['segment']['id']))
    return {'query': args.query, 'count': len(matches), 'items': matches,
            'boundary': '检索命中不是分镜批准；制作前仍须核对同一任务及锁定分镜'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.set_defaults(db=None)
    sub = parser.add_subparsers(dest='command', required=True)
    a = sub.add_parser('intake')
    a.add_argument('--project', type=Path, required=True)
    a.add_argument('--file', type=Path, required=True)
    a.add_argument('--role', choices=sorted(ROLES), default='unverified')
    a.add_argument('--title')
    a.add_argument('--product-name')
    a.add_argument('--provenance')
    a.add_argument('--inspection-scope')
    p = sub.add_parser('publish')
    p.add_argument('--cards', type=Path, required=True)
    f = sub.add_parser('find')
    f.add_argument('query')
    args = parser.parse_args()
    result = {'intake': intake, 'publish': publish, 'find': find}[args.command](args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
