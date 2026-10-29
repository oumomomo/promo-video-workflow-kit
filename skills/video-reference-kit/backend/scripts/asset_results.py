"""Versioned result submission through the existing asset database.

The disk queue is a retry journal, never a second queryable catalogue. A stream
belongs to a producer; updates require its current version. Project approvals
and rights gates are deliberately not writable through this result protocol.
"""
import asset_exclusion
import contextlib
import hashlib
import json
import os
import re
import sqlite3
import tempfile
from pathlib import Path


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


def init(db):
    db.executescript('''
    BEGIN IMMEDIATE;
    CREATE TABLE IF NOT EXISTS asset_result_versions(
      version TEXT PRIMARY KEY, record_id TEXT NOT NULL REFERENCES asset_records,
      producer TEXT NOT NULL, stream TEXT NOT NULL, parent TEXT,
      payload TEXT NOT NULL, created TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS asset_result_heads(
      record_id TEXT NOT NULL REFERENCES asset_records, producer TEXT NOT NULL,
      stream TEXT NOT NULL, version TEXT NOT NULL REFERENCES asset_result_versions,
      PRIMARY KEY(record_id,producer,stream));
    CREATE TABLE IF NOT EXISTS asset_result_receipts(
      request_id TEXT PRIMARY KEY, request_hash TEXT NOT NULL, receipt TEXT NOT NULL,
      created TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS asset_producer_ids(
      producer TEXT NOT NULL, external_id TEXT NOT NULL,
      record_id TEXT NOT NULL REFERENCES asset_records,
      PRIMARY KEY(producer,external_id));
    COMMIT;
    ''')
    db.commit()


def has_schema(db):
    return bool(db.execute("SELECT 1 FROM sqlite_master WHERE name='asset_result_heads'").fetchone())


def text(value, name):
    if not isinstance(value, str) or not value.strip() or len(value) > 1000:
        raise ValueError(f'{name} 必须是非空短文本')
    return value


def canonical(db, rid):
    if asset_exclusion.blocked(db,rid):
        raise ValueError('资产已排除，不允许通过此入口取用或更新')
    seen = set()
    while rid not in seen:
        seen.add(rid)
        alias = db.execute('SELECT record_id FROM asset_aliases WHERE alias=?', (rid,)).fetchone()
        if not alias:
            row = db.execute('SELECT * FROM asset_records WHERE id=?', (rid,)).fetchone()
            if row is None:
                raise ValueError('资产 ID 不存在')
            if json.loads(row['metadata']).get('retrievalExcluded'):
                raise ValueError('资产已排除，不允许通过此入口取用或更新')
            return row
        rid = alias[0]
    raise ValueError('资产别名形成循环')


def prepare(request, catalog):
    r = json.loads(encoded(request))
    if r.get('schemaVersion') != 1:
        raise ValueError('不支持的结果协议版本')
    for name in ('requestId', 'producer', 'stream'):
        text(r.get(name), name)
    asset = r.get('asset')
    if not isinstance(asset, dict):
        raise ValueError('缺少 asset')
    if not asset.get('id'):
        for name in ('externalId', 'title', 'kind'):
            text(asset.get(name), 'asset.' + name)
    if 'metadata' in asset or 'reviewStatus' in asset or 'rightsStatus' in asset:
        raise ValueError('结果登记不能修改审核或授权状态')
    docs = r.get('documents', [])
    if not isinstance(docs, list) or len(docs) > 100:
        raise ValueError('documents 必须为最多 100 个正文的列表')
    keys = set()
    for doc in docs:
        key = text(doc.get('key'), 'document.key')
        if key in keys:
            raise ValueError('正文 key 重复')
        keys.add(key)
        if 'body' in doc and 'path' in doc:
            raise ValueError('正文 body 和 path 只能指定一个')
        if 'path' in doc:
            p = Path(doc.pop('path')).resolve()
            if p.stat().st_size > 8 * 1024 * 1024:
                raise ValueError('正文超过 8 MiB，请作为文件对象登记')
            doc['body'] = p.read_text(encoding='utf-8')
            doc['sourcePath'] = str(p)
        if not isinstance(doc.get('body'), str) or len(doc['body'].encode()) > 8 * 1024 * 1024:
            raise ValueError('正文缺失或超过 8 MiB')
        if doc.get('format', '.md') not in ('.md', '.txt', '.json', '.csv', '.html'):
            raise ValueError('不支持的正文格式')
        doc.setdefault('format', '.md')
    files = r.get('files', [])
    if not isinstance(files, list) or len(files) > 100:
        raise ValueError('files 必须为最多 100 个对象的列表')
    for obj in files:
        p = Path(text(obj.get('path'), 'file.path')).resolve()
        expected = obj.get('sha256')
        actual = catalog.digest(p)
        if expected and expected != actual:
            raise ValueError('文件已改变，与提交的哈希不一致')
        obj.update(path=str(p), sha256=actual)
        text(obj.setdefault('role', 'source'), 'file.role')
    if not docs and not files and not r.get('attributes') and not r.get('sourceUri'):
        raise ValueError('结果没有正文、文件、属性或来源')
    if len(encoded(r).encode()) > 24 * 1024 * 1024:
        raise ValueError('一次提交超过 24 MiB，请拆分结果流')
    import asset_motion_results
    asset_motion_results.entry(r)
    import asset_audio_results
    asset_audio_results.item(r)
    return r


def read(db, rid, producer, stream, version=None):
    row = canonical(db, rid)
    rid = row['id']
    if not has_schema(db):
        raise ValueError('此资产尚无版本化结果')
    if version:
        found = db.execute('SELECT * FROM asset_result_versions WHERE version=? AND record_id=? AND producer=? AND stream=?',
                           (version, rid, producer, stream)).fetchone()
    else:
        found = db.execute('SELECT v.* FROM asset_result_heads h JOIN asset_result_versions v ON v.version=h.version WHERE h.record_id=? AND h.producer=? AND h.stream=?',
                           (rid, producer, stream)).fetchone()
    if not found:
        raise ValueError('未找到指定的结果版本')
    payload = json.loads(found['payload'])
    for doc in payload.get('documents', []):
        if 'body' not in doc:
            body = db.execute('SELECT body FROM asset_documents WHERE sha=?', (doc['sha256'],)).fetchone()
            if body is None:
                raise ValueError('正文版本缺失，不能用其他版本替代')
            doc['body'] = body[0]
    return {**dict(found), 'payload': payload}


def heads(db, rid):
    if not has_schema(db):
        return []
    return [dict(r) for r in db.execute('SELECT producer,stream,version FROM asset_result_heads WHERE record_id=? ORDER BY producer,stream', (rid,))]


def commit(db, r, catalog):
    request_hash = sha(encoded(r))
    db.execute('BEGIN IMMEDIATE')
    try:
        previous = db.execute('SELECT * FROM asset_result_receipts WHERE request_id=?', (r['requestId'],)).fetchone()
        if previous:
            if previous['request_hash'] != request_hash:
                raise ValueError('同一 requestId 被用于不同内容')
            receipt = json.loads(previous['receipt'])
            db.commit()
            return {**receipt, 'replayed': True}
        a, producer, stream = r['asset'], r['producer'], r['stream']
        bound = db.execute('SELECT record_id FROM asset_producer_ids WHERE producer=? AND external_id=?',
                           (producer, a.get('externalId', ''))).fetchone()
        row = canonical(db, a['id']) if a.get('id') else canonical(db, bound[0]) if bound else None
        source_files = [f for f in r.get('files', []) if f['role'] == 'source']
        for obj in r.get('files', []):
            excluded = db.execute(asset_exclusion.SQL + "SELECT 1 FROM asset_links l JOIN blocked b ON b.id=l.record_id WHERE l.sha=? LIMIT 1", (obj['sha256'],)).fetchone()
            if excluded:
                raise ValueError('文件对应已排除资产，不能通过换类型或新 ID 重新启用')
        if row is None and source_files:
            matches = db.execute("SELECT DISTINCT r.id FROM asset_links l JOIN asset_records r ON r.id=l.record_id WHERE l.sha=? AND l.role='source' AND r.kind=? AND r.id NOT IN (SELECT alias FROM asset_aliases)",
                                 (source_files[0]['sha256'], a['kind'])).fetchall()
            if len(matches) > 1:
                raise ValueError('同内容有多个逻辑资产，请明确 asset.id')
            if matches:
                row = canonical(db, matches[0][0])
        if row is not None and bound and canonical(db, bound[0])['id'] != row['id']:
            raise ValueError('externalId 已绑定另一条资产')
        if row is not None and a.get('kind', row['kind']) != row['kind']:
            raise ValueError('不可更改既有资产类型')
        rid = row['id'] if row else 'asset:' + sha(encoded([producer, a['externalId']]))
        old = db.execute('SELECT version FROM asset_result_heads WHERE record_id=? AND producer=? AND stream=?', (rid, producer, stream)).fetchone()
        actual = old[0] if old else None
        if r.get('baseVersion') != actual:
            raise ValueError(f'版本冲突：当前版本为 {actual}，请先读取再提交')
        # Imported claims remain claims; no status here can upgrade review/rights.
        if row is None:
            source_name = source_files[0].get('path', '') if source_files else ''
            catalog.record(db, rid, a['title'], a['kind'], {'reviewStatus': 'pending', 'producer': producer, 'sourceFilename': source_name},
                           a.get('platform', ''), a.get('category', ''), a.get('batchCategory', ''))
        elif a.get('category') or a.get('batchCategory'):
            catalog.record(db, rid, row['title'], row['kind'], json.loads(row['metadata']),
                           row['platform'], a.get('category', ''), a.get('batchCategory', ''), row['legacy_id'])
        if a.get('legacyId'):
            legacy = db.execute("SELECT 1 FROM library_items WHERE item_id=? AND entity_kind='reference_video'", (a['legacyId'],)).fetchone()
            if not legacy or (row['kind'] if row else a['kind']) != 'reference_video':
                raise ValueError('有效的工作台参考 ID 才能绑定已有审核记录')
            mapped = db.execute('SELECT record_id FROM asset_legacy_links WHERE legacy_id=?', (a['legacyId'],)).fetchone()
            if mapped and canonical(db, mapped[0])['id'] != rid and mapped[0] != 'legacy:' + a['legacyId']:
                raise ValueError('工作台编号已绑定另一资产，需先核对映射')
            db.execute('UPDATE asset_records SET legacy_id=? WHERE id=?', (a['legacyId'], rid))
            db.execute('INSERT OR REPLACE INTO asset_legacy_links VALUES(?,?)', (a['legacyId'], rid))
            alias = 'legacy:' + a['legacyId']
            if alias != rid and db.execute('SELECT 1 FROM asset_records WHERE id=?', (alias,)).fetchone():
                db.execute('INSERT OR REPLACE INTO asset_aliases VALUES(?,?)', (alias, rid))
        if a.get('externalId'):
            db.execute('INSERT OR IGNORE INTO asset_producer_ids VALUES(?,?,?)', (producer, a['externalId'], rid))
        for obj in r.get('files', []):
            actual_sha = catalog.register_file(db, obj['path'], rid, obj['role'])
            if actual_sha != obj['sha256']:
                raise ValueError('原文件已改变，保留待办但拒绝登记新内容')
        uri = r.get('sourceUri')
        if uri:
            text(uri, 'sourceUri')
            if uri.startswith(('https://', 'http://')):
                uri = catalog.normalize_url(uri)
            elif not re.match(r'^[a-z][a-z0-9+.-]*:', uri) or uri.startswith('file:'):
                raise ValueError('来源须为可移植 URI，不能是个人绝对路径')
            db.execute('INSERT OR IGNORE INTO asset_sources VALUES(?,?)', (rid, uri))
        payload = {k: v for k, v in r.items() if k not in ('requestId', 'baseVersion', 'asset')}
        payload['assetId'] = rid
        payload['documents'] = []
        for doc in r.get('documents', []):
            body_sha = sha(doc['body'])
            db.execute('INSERT OR IGNORE INTO asset_documents VALUES(?,?,?)', (body_sha, doc['body'], doc['format']))
            payload['documents'].append({**{k: v for k, v in doc.items() if k != 'body'}, 'sha256': body_sha})
        version = sha(encoded({'assetId': rid, 'parent': actual, 'payload': payload}))
        stamp = catalog.STAMP()
        db.execute('INSERT INTO asset_result_versions VALUES(?,?,?,?,?,?,?)', (version, rid, producer, stream, actual, encoded(payload), stamp))
        db.execute('INSERT INTO asset_result_heads VALUES(?,?,?,?) ON CONFLICT(record_id,producer,stream) DO UPDATE SET version=excluded.version', (rid, producer, stream, version))
        # Search/get use current managed bodies. Full historical bodies remain in
        # immutable result payloads and asset_documents, not competing current links.
        prefix = 'asset-result:' + sha(encoded([rid, producer, stream])) + ':'
        db.execute('DELETE FROM asset_document_links WHERE record_id=? AND substr(path,1,?)=?', (rid, len(prefix), prefix))
        for doc in r.get('documents', []):
            body_sha = sha(doc['body'])
            db.execute('INSERT OR IGNORE INTO asset_documents VALUES(?,?,?)', (body_sha, doc['body'], doc['format']))
            db.execute('INSERT INTO asset_document_links VALUES(?,?,?,?)', (rid, prefix + doc['key'], body_sha, stamp))
        import asset_motion_results
        asset_motion_results.project(db, r, rid, stamp)
        import asset_audio_results
        asset_audio_results.project(db, r, rid, stamp)
        receipt = {'state': 'committed', 'requestId': r['requestId'], 'assetId': rid, 'producer': producer,
                   'stream': stream, 'version': version, 'parent': actual, 'replayed': False,
                   'reviewChanged': False, 'cloudState': 'not_requested'}
        db.execute('INSERT INTO asset_result_receipts VALUES(?,?,?,?)', (r['requestId'], request_hash, encoded(receipt), stamp))
        db.commit()
        return receipt
    except Exception:
        db.rollback()
        raise


def queue_root(db_path):
    db_path = Path(db_path).resolve()
    return db_path.parent / 'asset-library' / 'pending-results' / sha(str(db_path))[:16]


def atomic_create(path, body):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temp = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(body)
            f.flush()
            os.fsync(f.fileno())
        try:
            os.link(temp, path)  # publish complete bytes without replacing a rival
        except FileExistsError:
            if path.read_text() != body:
                raise ValueError('待办 requestId 已存在且内容不同')
        dirfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        Path(temp).unlink(missing_ok=True)


def pending(db_path):
    out = []
    for p in sorted(queue_root(db_path).glob('*.json')):
        r = json.loads(p.read_text())
        out.append({'requestId': r['requestId'], 'producer': r['producer'], 'stream': r['stream'], 'state': 'pending_retry'})
    return {'items': out, 'count': len(out)}


def submit(db_path, catalog, request=None, retry_id=None):
    if retry_id is not None:
        path = queue_root(db_path) / (sha(retry_id) + '.json')
        r = json.loads(path.read_text())
        if r['requestId'] != retry_id:
            raise ValueError('待办身份不一致')
    else:
        r = prepare(request, catalog)
        path = queue_root(db_path) / (sha(r['requestId']) + '.json')
        atomic_create(path, encoded(r))
    try:
        with contextlib.closing(catalog.connect(db_path, True)) as db:
            init(db)
            result = commit(db, r, catalog)
        path.unlink(missing_ok=True)
        return result
    except Exception as error:
        return {'state': 'pending_retry', 'requestId': r['requestId'], 'error': str(error), 'type': type(error).__name__,
                'note': '结果已保全为待办；未宣称入库成功。修复原因后 retry，不要重新生成。'}
