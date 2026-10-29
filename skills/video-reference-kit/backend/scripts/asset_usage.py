"""Unified project adoption records; native workbench references remain authoritative."""
import contextlib,json
import asset_results
from pathlib import Path

def read(db,project_id):
    result=[]
    native_id=project_id
    if project_id.startswith('local-project:') and db.execute("SELECT 1 FROM sqlite_master WHERE name='projects'").fetchone():
        for p in db.execute('SELECT id,project_dir FROM projects'):
            if p['project_dir'] and 'local-project:'+asset_results.sha(str(Path(p['project_dir']).resolve()))[:24]==project_id:
                native_id=p['id'];break
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='revision_source_uses'").fetchone():
        result=[dict(r) for r in db.execute('''SELECT u.*,s.project_id FROM revision_source_uses u
            JOIN script_revisions s ON s.id=u.revision_id WHERE s.project_id=?''',(native_id,))]
    bound=db.execute('SELECT record_id FROM asset_producer_ids WHERE producer=? AND external_id=?',('project-adoption',project_id)).fetchone()
    ledgers=[]
    if bound:
        for h in asset_results.heads(db,bound[0]):
            if h['producer']=='project-adoption':ledgers.append(asset_results.read(db,bound[0],h['producer'],h['stream']))
    return dict(projectId=project_id,nativeReferences=result,ledgers=ledgers)

def submit(db_path,request,catalog):
    project_id=asset_results.text(request.get('projectId'),'projectId')
    scope=asset_results.text(request.get('scope'),'scope')
    body=request.get('ledger')
    if not isinstance(body,dict):raise ValueError('ledger must be an object')
    r=dict(schemaVersion=1,producer='project-adoption',stream=scope,
        asset=dict(externalId=project_id,title=request.get('title') or project_id,kind='project'),
        documents=[dict(key='adoption-ledger',body=asset_results.encoded(body),format='.json')])
    r['requestId']='usage:'+asset_results.sha(asset_results.encoded(r))
    try:
        connection=catalog.connect(db_path)
    except Exception:
        return asset_results.submit(db_path,catalog,request=r)
    with contextlib.closing(connection) as db:
        prior=db.execute('SELECT receipt FROM asset_result_receipts WHERE request_id=?',(r['requestId'],)).fetchone()
        if prior:return {**json.loads(prior[0]),'replayed':True}
        bound=db.execute('SELECT record_id FROM asset_producer_ids WHERE producer=? AND external_id=?',(r['producer'],project_id)).fetchone()
        if bound:
            heads=asset_results.heads(db,bound[0]);head=next((h for h in heads if h['producer']==r['producer'] and h['stream']==scope),None)
            if head:r['baseVersion']=head['version']
    return asset_results.submit(db_path,catalog,request=r)
