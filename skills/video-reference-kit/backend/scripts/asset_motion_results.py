"""Transactional, conservative workflow projection for newly submitted motion recipes."""
import json
import hashlib
from pathlib import Path


def entry(request):
    if request['producer'] != 'video-motion-library' or request['stream'] != 'recipe':
        return None
    a = request['asset']
    e = request.get('attributes', {}).get('motionEntry')
    if not isinstance(e, dict) or a.get('kind') != 'motion_capability':
        raise ValueError('动效提交缺少配方合同')
    for key in ('id', 'card', 'summary', 'category'):
        if not isinstance(e.get(key), str) or not e[key].strip():
            raise ValueError('动效字段缺失：' + key)
    if a.get('externalId') != e['id'] or e['id'].startswith(('VML:', 'EME-', 'MV:')):
        raise ValueError('原创使用未加命名空间的独立编号')
    for key in ('tags', 'demos'):
        if not isinstance(e.get(key, []), list) or any(not isinstance(x, str) for x in e.get(key, [])):
            raise ValueError('动效列表字段无效：' + key)
    for key in ('style_key','style_label','style_description','updated_at','source','preview','use','intention','duration','energy','origin','status','note','category_zh'):
        if key in e and not isinstance(e[key], str):
            raise ValueError('动效文本字段无效：' + key)
    files = {f['path'] for f in request.get('files', [])}
    for path in ([e['source']] if e.get('source') else []) + e.get('demos', []):
        if not Path(path).is_absolute() or path not in files:
            raise ValueError('动效源码必须通过文件哈希登记：' + path)
    return e


def project(db, request, rid, stamp):
    e = entry(request)
    if e is None:
        return
    item_id = 'VML:' + e['id']
    existing = db.execute('SELECT * FROM library_items WHERE item_id=?', (item_id,)).fetchone()
    mapped = db.execute('SELECT record_id FROM asset_legacy_links WHERE legacy_id=?', (item_id,)).fetchone()
    if existing and (not mapped or mapped[0] != rid):
        raise ValueError('原创编号已存在，不能覆盖既有动效：' + item_id)
    # Submitted maturity is evidence, never human approval or permission to render.
    source = e.get('source', '')
    demos = e.get('demos', [])
    p = dict(motionId=item_id, rawId=e['id'], humanName=e.get('style_label') or e['id'],
        humanNameZh=e.get('style_label') or e['id'], category=e['category'], categoryZh=e.get('category_zh', e['category']),
        summary=e['summary'], use=e.get('use', ''), narrativeIntent=e.get('intention', ''),
        duration=e.get('duration', ''), energy=e.get('energy', ''), origin=e.get('origin', 'custom'),
        maturity='candidate', maturityZh='候选·未验收', declaredMaturity=e.get('status', 'candidate'),
        legacyIdentity={k:e.get(k, '') for k in ('card','style_key','style_label','style_description','updated_at')},
        source=dict(declared=source,localPath=source or None,available=bool(source)),
        demo=dict(declared=demos,localPaths=demos,availablePaths=demos,available=bool(demos)),
        preview=dict(declared=e.get('preview',''),localPath=None,available=False),still={},reviewPreview=None,
        callMode='reference_or_remix',executionStatus='candidate_unverified',promptTemplate=e['summary'],
        compositionId=None,workbenchRenderer=None,verticalReady=False,note=e.get('note',''))
    p['implementationHashes'] = {f['path']: f['sha256'] for f in request.get('files', [])}
    body=json.dumps(p,ensure_ascii=False,separators=(',',':'))
    digest=hashlib.sha256(body.encode()).hexdigest()
    version='libv_'+hashlib.sha256((item_id+':'+digest).encode()).hexdigest()[:18]
    if not existing:
        db.execute('''INSERT INTO library_items
          (item_id,source_system,external_id,entity_kind,title,source_language,analysis_language,language_scope,
           source_review_status,review_status,capability_status,rights_status,ai_status,tags_json,source_path,
           source_url,current_version_id,created_at,updated_at,last_seen_at)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
          (item_id,'video_motion_library',item_id,'motion_capability',p['humanNameZh'],'unknown','zh-CN','language_independent',
           'candidate','candidate','blocked_auto_execution','unknown','eligible',json.dumps(e.get('tags',[]),ensure_ascii=False),
           source or None,None,None,stamp,stamp,stamp))
    db.execute('INSERT OR IGNORE INTO library_item_versions VALUES(?,?,?,?,?,?,?)',
               (version,item_id,digest,body,'[]',e['summary'],stamp))
    # A new recipe revision may not silently inherit an executable renderer.
    db.execute('UPDATE library_items SET current_version_id=?,title=?,source_path=?,capability_status=?,updated_at=? WHERE item_id=?',
               (version,p['humanNameZh'],source or None,'blocked_auto_execution',stamp,item_id))
    db.execute('INSERT OR IGNORE INTO asset_legacy_links VALUES(?,?)',(item_id,rid))
    db.execute('UPDATE asset_records SET legacy_id=? WHERE id=?',(item_id,rid))
