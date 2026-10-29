"""Audio catalog projection in the same transaction as the durable receipt."""
import json
import hashlib
import asset_exclusion
from pathlib import Path


def item(request):
    if request['producer'] != 'audio-library' or not request['stream'].startswith('catalog:'):
        return None
    i = request.get('attributes', {}).get('workflowItem')
    if not isinstance(i, dict) or i.get('entityKind') not in ('music_track','sound_effect'):
        raise ValueError('invalid audio workflow item')
    p = i['compactPayload']
    if request['asset'].get('externalId') != i['sourceId'] or request['asset'].get('kind') != i['entityKind']:
        raise ValueError('audio identity mismatch')
    sources = [f for f in request.get('files',[]) if f['role']=='source']
    if len(sources)!=1 or sources[0]['sha256']!=p.get('sha256') or Path(sources[0]['path']).resolve()!=Path(p.get('localPath','')).resolve():
        raise ValueError('audio source must match verified file')
    rights = p.get('rights',{})
    provenance = p.get('provenance',{})
    licensed = (rights.get('status')=='licensed' and rights.get('license') and rights.get('evidence')
        and str(rights.get('licenseUrl','')).startswith(('https://','http://'))
        and str(rights.get('sourceUrl','')).startswith(('https://','http://'))
        and provenance.get('origin')=='licensed_download' and provenance.get('evidenceComplete') is True)
    owned = (rights.get('status')=='owned' and rights.get('license')=='project-owned-procedural-audio'
        and rights.get('evidence') and provenance.get('origin')=='internal_programmatic_generation'
        and provenance.get('sourceInputs')==[] and provenance.get('recipeId') and provenance.get('generatorScript'))
    if i.get('rightsStatus') in ('licensed','owned') and not (licensed if i['rightsStatus']=='licensed' else owned):
        raise ValueError('audio rights evidence incomplete')
    if i.get('aiEligible') and (not (licensed or owned) or p.get('catalogStatus')!='available'):
        raise ValueError('audio automatic-use gate failed')
    return i


def project(db,request,rid,stamp):
    i=item(request)
    if i is None:return
    iid=i['sourceId']; p=i['compactPayload']
    if iid in asset_exclusion.workflow_ids(db):raise ValueError('声音已排除')
    old=db.execute('SELECT * FROM library_items WHERE item_id=?',(iid,)).fetchone()
    if old:
        if old['entity_kind']!=i['entityKind']:raise ValueError('audio type collision')
        previous=json.loads(db.execute('SELECT payload_json FROM library_item_versions WHERE version_id=?',(old['current_version_id'],)).fetchone()[0])
        if previous.get('sha256')!=p['sha256']:raise ValueError('audio_asset_bytes_changed: 相同编号不可替换文件')
    body=json.dumps(p,ensure_ascii=False,separators=(',',':'))
    digest=hashlib.sha256(body.encode()).hexdigest()
    vid='libv_'+hashlib.sha256((iid+':'+digest).encode()).hexdigest()[:18]
    if not old:
        db.execute('''INSERT INTO library_items
        (item_id,source_system,external_id,entity_kind,title,source_language,analysis_language,language_scope,
         source_review_status,review_status,capability_status,rights_status,ai_status,tags_json,source_path,
         source_url,current_version_id,created_at,updated_at,last_seen_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
         (iid,i['sourceSystem'],iid,i['entityKind'],i['title'],'none','zh-CN','language_independent',
          i['reviewStatus'],i['reviewStatus'],i['capabilityStatus'],i['rightsStatus'],'eligible' if i.get('aiEligible') else 'blocked',
          json.dumps(i.get('tags',[]),ensure_ascii=False),p['localPath'],i.get('sourceUrl'),None,stamp,stamp,stamp))
    db.execute('INSERT OR IGNORE INTO library_item_versions VALUES(?,?,?,?,?,?,?)',(vid,iid,digest,body,'[]',i['title'],stamp))
    db.execute('''UPDATE library_items SET current_version_id=?,title=?,source_path=?,source_url=?,capability_status=?,
        ai_status=CASE WHEN ai_override IS NULL THEN ? ELSE ai_status END,updated_at=? WHERE item_id=?''',
        (vid,i['title'],p['localPath'],i.get('sourceUrl'),i['capabilityStatus'],'eligible' if i.get('aiEligible') else 'blocked',stamp,iid))
    mapped=db.execute('SELECT record_id FROM asset_legacy_links WHERE legacy_id=?',(iid,)).fetchone()
    if mapped and mapped[0]!=rid:
        if mapped[0]!='legacy:'+iid:raise ValueError('audio ID already bound')
        db.execute('INSERT OR REPLACE INTO asset_aliases VALUES(?,?)',(mapped[0],rid))
    db.execute('INSERT OR REPLACE INTO asset_legacy_links VALUES(?,?)',(iid,rid))
    db.execute('UPDATE asset_records SET legacy_id=? WHERE id=?',(iid,rid))
