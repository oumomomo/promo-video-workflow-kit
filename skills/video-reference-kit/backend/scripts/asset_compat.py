"""Legacy video-flow asset commands, backed exclusively by the shared database."""
import contextlib
import json
from pathlib import Path
import asset_results as results


def run(db_path, command, options, catalog):
    with contextlib.closing(catalog.connect(db_path)) as db:
        if command == 'library-init':
            return {'ok': True, 'mode': 'unified', 'createdLibrary': False,
                    'note': '已使用现有统一库；没有创建 registry.json 或新素材库。', 'stats': catalog.stats(db)}
        if command == 'asset-search':
            # Page the shared search, then retain the legacy status filter without
            # treating a declared recommendation as approval or usage permission.
            items = []
            offset = 0
            while True:
                page = catalog.search(db, options.get('query', ''), limit=100, offset=offset,
                                      scope=options.get('scope', 'all'))
                for item in page['items']:
                    if options.get('status'):
                        hs = results.heads(db, item['id'])
                        legacy = next((h for h in hs if h['producer'] == 'video-flow' and h['stream'] == 'registration'), None)
                        if not legacy:
                            continue
                        attrs = results.read(db, item['id'], 'video-flow', 'registration')['payload'].get('attributes', {})
                        if attrs.get('declaredStatus') != options['status']:
                            continue
                    items.append(item)
                offset += len(page['items'])
                if offset >= page['count'] or not page['items']:
                    break
            return {'ok': True, 'mode': 'unified', 'count': len(items), 'assets': items}
    if command != 'asset-register':
        raise ValueError('不支持的旧素材命令')
    for key in ('id', 'name', 'type', 'uri', 'license'):
        results.text(options.get(key), '--' + key)
    uri = options['uri']
    if uri.startswith(('/', '~', 'file:')):
        raise ValueError('--uri 须为可移植 URI')
    status = options.get('status', 'candidate')
    if status not in {'candidate', 'tested', 'recommended', 'deprecated', 'review-only'}:
        raise ValueError('无效的旧素材状态')
    kind = {'reference': 'reference_video', 'reference-video': 'reference_video', 'motion': 'motion_capability'}.get(options['type'], options['type'])
    external = options['id']
    # Existing registries are migration sources, not writable destinations.
    old_registry = Path(options['library']).expanduser() / 'registry.json' if options.get('library') else None
    if old_registry and old_registry.is_file():
        library_id = json.loads(old_registry.read_text()).get('libraryId')
        if library_id:
            external = str(library_id) + ':' + external
    attrs = {'legacyId': options['id'], 'declaredStatus': status, 'declaredLicense': options['license'],
             'tags': [s.strip() for s in options.get('tags', '').split(',') if s.strip()],
             'usageScope': options.get('scope'), 'owner': options.get('owner'), 'previewUri': options.get('preview'),
             'claimedSourceSha256': options.get('sha256'),
             'note': '旧命令声明，不构成已核权、人工批准或推荐效果验收'}
    r = {'schemaVersion': 1, 'producer': 'video-flow', 'stream': 'registration',
         'asset': {'externalId': external, 'title': options['name'], 'kind': kind},
         'sourceUri': uri, 'attributes': attrs,
         'documents': [{'key': 'registration', 'format': '.json', 'body': results.encoded({'title': options['name'], **attrs})}]}
    if options.get('source-file'):
        r['files'] = [{'path': str(Path(options['source-file']).resolve()), 'sha256': options.get('sha256')}]
    if options.get('base-version'):
        r['baseVersion'] = options['base-version']
    r['requestId'] = 'video-flow:' + results.sha(results.encoded(r))
    receipt = results.submit(db_path, catalog, r)
    if receipt['state'] == 'committed':
        return {'ok': True, 'mode': 'unified', **receipt, 'note': '已写统一库；旧 registry.json 未修改。'}
    return {'ok': False, 'mode': 'unified', **receipt}
