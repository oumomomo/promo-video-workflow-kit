#!/usr/bin/env python3
# Distribution change: --db must be explicit; no implicit database fallback.
"""Unified asset registry. Uses the workbench SQLite file; media stays external."""
import argparse, contextlib, datetime, hashlib, json, mimetypes, os, re, sqlite3, sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
sys.path.insert(0,str(Path(__file__).resolve().parent))
from asset_classification import infer, enrich
from asset_summaries import import_summaries
import asset_exclusion
import asset_results
import asset_workflow_catalog
import asset_compat
import asset_usage
APP = Path(__file__).resolve().parents[1]
DEFAULT_DB = APP / 'data/creator-workbench.sqlite'
SKIP = {'node_modules','vendor','upstream','dist','build','.git','.venv','venv','__pycache__','browser-sessions','asr-models','asset-library','视频拆解总目录-20260918'}
MEDIA = {'.mp4':'video','.mov':'video','.webm':'video','.mkv':'video','.wav':'audio','.mp3':'audio','.m4a':'audio','.flac':'audio','.aac':'audio','.png':'image','.jpg':'image','.jpeg':'image','.webp':'image','.svg':'image','.ttf':'font','.otf':'font','.woff2':'font','.blend':'project','.aep':'project','.psd':'project','.ai':'project'}
EVIDENCE_ROLES = {'product_ui_original', 'feedback_context', 'conversation_context', 'production_context', 'unverified'}
PRODUCT_UI_KINDS = {'image', 'reference_image', 'video', 'reference_video'}
STAMP = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
def dumps(x): return json.dumps(x,ensure_ascii=False,sort_keys=True)
def digest(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def key(s): return hashlib.sha256(s.encode()).hexdigest()
def connect(path,write=False):
    db=sqlite3.connect(Path(path).resolve().as_uri()+('?mode=rw' if write else '?mode=ro'),uri=True,timeout=30)
    db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON');db.execute('PRAGMA busy_timeout=30000')
    return db
def init(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS asset_catalog_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    INSERT OR IGNORE INTO asset_catalog_meta VALUES('schema_version','1');
    CREATE TABLE IF NOT EXISTS asset_records(id TEXT PRIMARY KEY,title TEXT NOT NULL,kind TEXT NOT NULL,category TEXT NOT NULL,category_origin TEXT NOT NULL,platform TEXT NOT NULL,metadata TEXT NOT NULL,legacy_id TEXT,updated TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS asset_objects(sha TEXT PRIMARY KEY CHECK(length(sha)=64),size INTEGER NOT NULL,mime TEXT NOT NULL,created TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS asset_locations(path TEXT PRIMARY KEY,sha TEXT NOT NULL REFERENCES asset_objects,mtime_ns INTEGER NOT NULL,device INTEGER,inode INTEGER,verified TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS asset_locations_sha ON asset_locations(sha);
    CREATE TABLE IF NOT EXISTS asset_links(record_id TEXT NOT NULL REFERENCES asset_records,sha TEXT NOT NULL REFERENCES asset_objects,role TEXT NOT NULL,PRIMARY KEY(record_id,sha,role));
    CREATE TABLE IF NOT EXISTS asset_documents(sha TEXT PRIMARY KEY,body TEXT NOT NULL,format TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS asset_document_links(record_id TEXT NOT NULL REFERENCES asset_records,path TEXT NOT NULL,sha TEXT NOT NULL REFERENCES asset_documents,created TEXT NOT NULL,PRIMARY KEY(record_id,path,sha));
    CREATE TABLE IF NOT EXISTS asset_document_sections(record_id TEXT NOT NULL REFERENCES asset_records,source_sha TEXT NOT NULL REFERENCES asset_documents,excerpt_sha TEXT NOT NULL REFERENCES asset_documents,source_path TEXT NOT NULL,start_line INTEGER NOT NULL,end_line INTEGER NOT NULL,label TEXT NOT NULL,PRIMARY KEY(record_id,source_sha,start_line,end_line));
    CREATE INDEX IF NOT EXISTS asset_document_record ON asset_document_links(record_id);
    CREATE TABLE IF NOT EXISTS asset_sources(record_id TEXT NOT NULL REFERENCES asset_records,uri TEXT NOT NULL,PRIMARY KEY(record_id,uri));
    CREATE TABLE IF NOT EXISTS asset_legacy_links(legacy_id TEXT PRIMARY KEY,record_id TEXT NOT NULL REFERENCES asset_records);
    CREATE TABLE IF NOT EXISTS asset_aliases(alias TEXT PRIMARY KEY REFERENCES asset_records,record_id TEXT NOT NULL REFERENCES asset_records);
    CREATE TABLE IF NOT EXISTS asset_events(id INTEGER PRIMARY KEY,record_id TEXT,action TEXT NOT NULL,payload TEXT NOT NULL,created TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS asset_cloud_receipts(sha TEXT PRIMARY KEY REFERENCES asset_objects,receipt TEXT NOT NULL,verified TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS asset_migration_issues(path TEXT PRIMARY KEY,reason TEXT NOT NULL,updated TEXT NOT NULL);
    ''');db.commit()

def normalize_url(raw):
    u=urlsplit(raw);host=(u.hostname or '').lower().removeprefix('www.')
    if u.scheme not in ('http','https') or u.username or u.password: raise ValueError('需要不带凭据的 http/https 来源地址')
    if host in ('x.com','twitter.com','mobile.twitter.com'):
        m=re.search(r'/status/(\d+)',u.path)
        if m:return 'https://x.com/i/status/'+m[1]
    if host in ('xiaohongshu.com','www.xiaohongshu.com'):
        m=re.search(r'/(?:explore|discovery/item)/([a-f0-9]+)',u.path)
        if m:return 'https://xiaohongshu.com/explore/'+m[1]
    # Keep media selectors and signed semantic query fields; remove known tracking only.
    q=[(k,v) for k,v in parse_qsl(u.query) if not k.lower().startswith('utm_') and k.lower() not in {'xsec_token','xsec_source','share_token','share_source'}]
    return urlunsplit(('https',host,u.path.rstrip('/') or '/',urlencode(sorted(q)),''))

def classify(platform='',single='',batch='',existing=None):
    if single:return single,'user_single'
    if existing and existing['category_origin']=='user_single':return existing['category'],'user_single'
    if batch:return batch,'user_batch'
    if existing and existing['category_origin'].startswith('user_'):return existing['category'],existing['category_origin']
    if platform in ('抖音','小红书'):return '短视频参考','user_platform_convention'
    return (existing['category'],existing['category_origin']) if existing else ('待分类','unclassified')

def record(db,rid,title,kind,metadata=None,platform='',single='',batch='',legacy=None,classification_override=None):
    old=db.execute('SELECT * FROM asset_records WHERE id=?',(rid,)).fetchone()
    incoming=metadata or {}
    if kind in ('video','reference_video') and (kind=='video' or platform=='本地制作' or incoming.get('evidenceRole')=='production_context') and incoming.get('evidenceRole')!='product_ui_original':
        if re.search(r'样片|短样|验证版|粗剪|候选|审片|审看|非正式成片|(?i:production|candidate|preview|review|probe|draft|validation)',title+' '+single+' '+batch) or incoming.get('evidenceRole')=='production_context':
            raise ValueError('样片、候选和粗剪不进入素材库；仅在项目目录保留。只有用户明确指定的成片才归档。')
    if old and json.loads(old['metadata']).get('archiveRemoved'):
        raise ValueError('此样片已按用户要求移除，禁止重新归档')

    if legacy is None and old:legacy=old['legacy_id']
    category,origin=classify(platform,single,batch,old)
    metadata=dict(metadata or {})
    previous=json.loads(old['metadata']) if old else {}
    for role_field in ('evidenceRole','evidenceRoleBasis'):
        if role_field in previous:
            metadata.setdefault(role_field,previous[role_field])
    if kind in ('image','reference_image') and metadata.get('evidenceRole') in (None,'unverified'):
        filename=str(metadata.get('sourceFilename') or metadata.get('firstPath') or '')
        if any(term in (title+' '+Path(filename).name).lower() for term in ('feedback','反馈')):
            metadata['evidenceRole']='feedback_context'
            metadata['evidenceRoleBasis']='explicit feedback title or source filename; visual content not individually reviewed'
            category,origin='产品反馈截图','inferred_feedback_role'
    if previous.get('evidenceRole')=='feedback_context' and metadata.get('evidenceRole')=='feedback_context' and old:
        category,origin=old['category'],old['category_origin']
    if kind in ('video','reference_video') and (metadata.get('evidenceRole')=='production_context' or '非正式成片' in title or (platform=='本地制作' and category=='视频生产候选') or ('分镜粗剪' in title and metadata.get('producer'))):
        kind='video';category='项目过程存档';origin='production_role_guard'
        metadata['evidenceRole']='production_context'
        metadata['evidenceRoleBasis']='明确标注的验证样片或制作粗剪，仅供项目追溯，不作为可复用参考'
    suggested,evidence=infer(rid,title,kind,metadata)
    if category=='待分类' and origin=='unclassified':
        category=suggested;origin='content_evidence' if evidence['level']=='content' else 'asset_role' if category!='待分类' else 'unclassified'
    evidence=classification_override or previous.get('classification',evidence)
    if origin.startswith('user_'):
        category_basis={'user_single':'用户指定单条用途','user_batch':'用户指定批次用途','user_platform_convention':'用户约定：抖音、小红书默认作为短视频参考'}.get(origin,origin)
        evidence={**evidence,'categoryBasis':category_basis}
        if classification_override is None:evidence['basis']=category_basis
    metadata['classification']=enrich(metadata,evidence)
    values=(rid,title,kind,category,origin,platform,dumps(metadata),legacy,STAMP())
    if old and tuple(old[k] for k in ('title','kind','category','category_origin','platform','metadata','legacy_id'))==values[1:8]:return rid
    if old: db.execute('INSERT INTO asset_events(record_id,action,payload,created) VALUES(?,?,?,?)',(rid,'record_before_update',dumps(dict(old)),STAMP()))
    db.execute('INSERT INTO asset_records VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,kind=excluded.kind,category=excluded.category,category_origin=excluded.category_origin,platform=excluded.platform,metadata=excluded.metadata,legacy_id=excluded.legacy_id,updated=excluded.updated',values)
    return rid

def read_classification(path):
    p=Path(path)
    if p.stat().st_size>1024*1024:raise ValueError('classification file exceeds 1 MiB')
    data=json.loads(p.read_text())
    if not isinstance(data,dict):raise ValueError('classification must be an object')
    subtype=data.get('subtype');tags=data.get('tags');basis=data.get('basis');scope=data.get('inspectionScope')
    if not isinstance(subtype,str) or not subtype.strip() or len(subtype)>100:raise ValueError('classification subtype required (max 100 chars)')
    if not isinstance(tags,list) or len(tags)>20 or any(not isinstance(t,str) or not t.strip() or len(t)>60 for t in tags):raise ValueError('classification tags must be a list of up to 20 nonempty labels')
    if not isinstance(basis,str) or not basis.strip() or len(basis)>300:raise ValueError('classification basis required (max 300 chars)')
    if not isinstance(scope,str) or not scope.strip() or len(scope)>500:raise ValueError('classification inspectionScope required (max 500 chars)')
    return {'version':1,'level':'content','subtype':subtype.strip(),'tags':[t.strip() for t in tags],
            'basis':basis.strip(),'inspectionScope':scope.strip(),'evidenceFileSha256':digest(p)}

def issue(db,path,reason):db.execute('INSERT OR REPLACE INTO asset_migration_issues VALUES(?,?,?)',(str(path),reason,STAMP()))
def register_file(db,path,rid=None,role='source'):
    p=Path(path).absolute()
    if not p.is_file():issue(db,p,'missing');return None
    before=p.stat();prior=db.execute('SELECT * FROM asset_locations WHERE path=?',(str(p),)).fetchone()
    if prior and (prior['mtime_ns'],prior['device'],prior['inode'])==(before.st_mtime_ns,before.st_dev,before.st_ino):
        obj=db.execute('SELECT * FROM asset_objects WHERE sha=?',(prior['sha'],)).fetchone()
        if obj['size']==before.st_size:
            sha=prior['sha']
        else:sha=digest(p)
    else:sha=digest(p)
    after=p.stat()
    if (before.st_size,before.st_mtime_ns,before.st_ino)!=(after.st_size,after.st_mtime_ns,after.st_ino):
        issue(db,p,'changed_during_read');return None
    db.execute('INSERT OR IGNORE INTO asset_objects VALUES(?,?,?,?)',(sha,before.st_size,mimetypes.guess_type(p.name)[0] or 'application/octet-stream',STAMP()))
    db.execute('INSERT OR REPLACE INTO asset_locations VALUES(?,?,?,?,?,?)',(str(p),sha,before.st_mtime_ns,before.st_dev,before.st_ino,STAMP()))
    db.execute('DELETE FROM asset_migration_issues WHERE path=?',(str(p),))
    if rid:db.execute('INSERT OR IGNORE INTO asset_links VALUES(?,?,?)',(rid,sha,role))
    return sha

def document(db,rid,path):
    p=Path(path)
    if p.is_dir():
        for base,dirs,files in os.walk(p,followlinks=False):
            dirs[:]=[d for d in dirs if d not in SKIP and not d.startswith('.') and len((Path(base)/d).relative_to(p).parts)<5]
            for name in files:
                child=Path(base)/name
                if child.suffix.lower() in {'.md','.txt','.json','.html'}:document(db,rid,child)
        db.execute('DELETE FROM asset_migration_issues WHERE path=?',(str(p),));return
    if not p.is_file():issue(db,p,'missing_document');return
    if p.stat().st_size>8*1024*1024:issue(db,p,'document_over_8MiB_kept_as_file');register_file(db,p,rid,'document');return
    raw=p.read_bytes()
    try: body=raw.decode('utf-8')
    except UnicodeDecodeError:
        register_file(db,p,rid,'binary_evidence');return
    sha=hashlib.sha256(raw).hexdigest()
    db.execute('INSERT OR IGNORE INTO asset_documents VALUES(?,?,?)',(sha,body,p.suffix.lower()))
    db.execute('INSERT OR IGNORE INTO asset_document_links VALUES(?,?,?,?)',(rid,str(p.absolute()),sha,STAMP()))
    db.execute('DELETE FROM asset_migration_issues WHERE path=?',(str(p),))

def import_inventory(db,path):
    data=json.loads(Path(path).read_text()); ids={r[0] for r in db.execute('SELECT item_id FROM library_items')}
    for row in data['items']:
        rid='ref:'+row['id'];platform=''
        hay=' '.join(row.get('urls',[]))+' '+row['id']+' '+row['group']
        if 'xiaohongshu' in hay or 'xhs:' in hay or '小红书' in hay:platform='小红书'
        elif 'douyin' in hay or row['id'].startswith('dy:'):platform='抖音'
        elif 'x.com' in hay:platform='X'
        legacy=row['id'] if row['id'] in ids else None
        record(db,rid,row['title'],'reference_video',row,platform,legacy=legacy)
        for url in row.get('urls',[]):
            try:db.execute('INSERT OR IGNORE INTO asset_sources VALUES(?,?)',(rid,normalize_url(url)))
            except ValueError:pass
        for p in row.get('media',[]):register_file(db,p,rid)
        for p in row.get('reports',[]):document(db,rid,p)
        db.commit()
    for row in data.get('reports',[]):
        p=row['path']
        if not db.execute('SELECT 1 FROM asset_document_links WHERE path=?',(p,)).fetchone():
            rid='doc:'+key(p);record(db,rid,row.get('title') or Path(p).stem,'analysis_document',{'sourcePath':p});document(db,rid,p)
    db.commit();return stats(db)

def scan(db,root):
    root=Path(root).resolve();count=0;errors=0
    for base,dirs,files in os.walk(root,followlinks=False):
        dirs[:]=[x for x in dirs if x not in SKIP and not x.startswith('.') and not (Path(base)/x).is_symlink()]
        for name in files:
            p=Path(base)/name;ext=p.suffix.lower()
            if p.is_symlink() or ext not in MEDIA:continue
            # Generated frame series are inventoried separately, not promoted to reusable artwork.
            is_frame=bool(re.search(r'(?:^|/)(?:preview-frames|frames|keyframes|analysis_frames|analysis-frames)(?:/|$)',str(p)))
            try:
                sha=register_file(db,p)
                if not sha:continue
                if not db.execute('SELECT 1 FROM asset_links WHERE sha=?',(sha,)).fetchone():
                    rid='file:'+sha
                    kind='frame_evidence' if is_frame else MEDIA[ext]
                    record(db,rid,p.stem,kind,{'firstPath':str(p),'project':p.relative_to(root).parts[0],'rights':'unknown','reviewStatus':'unreviewed'})
                    db.execute('INSERT OR IGNORE INTO asset_links VALUES(?,?,?)',(rid,sha,'evidence' if is_frame else 'unclassified_file'))
                count+=1
                if count%500==0:db.commit();print(dumps({'scanned':count}),file=sys.stderr,flush=True)
            except (OSError,ValueError) as e:issue(db,p,str(e));errors+=1
    db.commit();return {'scanned':count,'errors':errors,**stats(db)}

def stats(db):
    n=lambda table:db.execute('SELECT count(*) FROM '+table).fetchone()[0]
    return {'records':db.execute('SELECT count(*) FROM asset_records WHERE id NOT IN (SELECT alias FROM asset_aliases)').fetchone()[0],'objects':n('asset_objects'),'locations':n('asset_locations'),'documents':n('asset_documents'),'cloudVerified':n('asset_cloud_receipts'),'issues':n('asset_migration_issues'),'kinds':dict(db.execute('SELECT kind,count(*) FROM asset_records WHERE id NOT IN (SELECT alias FROM asset_aliases) GROUP BY kind')),'categories':[dict(r) for r in db.execute('SELECT kind,category,count(*) AS count FROM asset_records WHERE id NOT IN (SELECT alias FROM asset_aliases) GROUP BY kind,category ORDER BY count DESC')],'uniqueBytes':db.execute('SELECT coalesce(sum(size),0) FROM asset_objects').fetchone()[0]}

def sync_workbench(db):
    linked={r['legacy_id']:r['id'] for r in db.execute('SELECT id,legacy_id FROM asset_records WHERE legacy_id IS NOT NULL AND id NOT LIKE "legacy:%"')}
    for row in db.execute('SELECT * FROM library_items').fetchall():
        target=linked.get(row['item_id'])
        if not target and row['entity_kind']=='reference_video':
            candidate='ref:dy:'+row['item_id'][3:] if re.fullmatch(r'DY-\d+',row['item_id']) else ''
            if candidate and db.execute('SELECT 1 FROM asset_records WHERE id=?',(candidate,)).fetchone():target=candidate
            if not target and row['source_url']:
                matches=db.execute('SELECT DISTINCT s.record_id FROM asset_sources s JOIN asset_records r ON r.id=s.record_id WHERE s.uri=? AND r.kind="reference_video" AND r.id LIKE "ref:%"',(normalize_url(row['source_url']),)).fetchall()
                if len(matches)==1:target=matches[0][0]
        if target:
            db.execute('INSERT OR REPLACE INTO asset_legacy_links VALUES(?,?)',(row['item_id'],target))
            db.execute('UPDATE asset_records SET legacy_id=coalesce(legacy_id,?) WHERE id=?',(row['item_id'],target))
            alias='legacy:'+row['item_id']
            if db.execute('SELECT 1 FROM asset_records WHERE id=?',(alias,)).fetchone():db.execute('INSERT OR REPLACE INTO asset_aliases VALUES(?,?)',(alias,target))
            continue
        platform='抖音' if row['source_system']=='douyin_pipeline' else 'X' if row['source_system']=='x_reference' else ''
        record(db,'legacy:'+row['item_id'],row['title'],row['entity_kind'],{'sourceSystem':row['source_system'],'tags':json.loads(row['tags_json']),'reviewStatus':row['review_status'],'rightsStatus':row['rights_status']},platform,legacy=row['item_id'])
        db.execute('INSERT OR REPLACE INTO asset_legacy_links VALUES(?,?)',(row['item_id'],'legacy:'+row['item_id']))
    db.commit();return stats(db)

def project_manifests(db,root):
    root=Path(root).resolve();count=0
    for project in sorted(root.iterdir()):
        if not project.is_dir() or project.name in SKIP or project.name.startswith('.'):continue
        paths=[]
        for base,dirs,files in os.walk(project,followlinks=False):
            dirs[:]=[d for d in dirs if d not in SKIP and not d.startswith('.') and not (Path(base)/d).is_symlink()]
            for name in files:
                p=Path(base)/name
                if p.is_symlink():continue
                if name in {'package.json','package-lock.json','pnpm-lock.yaml','README.md','archive.json','handoff.md','annotations.json','shots.json','motion-selection.json','visual-design-contract.json'} or (p.suffix=='.json' and ('manifest' in name or 'registry' in name)):
                    paths.append(p)
        if not paths:continue
        rid='project:'+key(str(project));record(db,rid,project.name,'project',{'root':str(project),'reviewStatus':'unreviewed','scope':'manifests_and_selected_sources','note':'账本登记；未完成完整工程恢复验证'})
        for p in paths:document(db,rid,p);count+=1
        db.commit()
    return {'projectDocuments':count,**stats(db)}

def attach_storage_times(db,items):
    """Recover registration time from record history, never from media creation time."""
    if not items:return
    by_id={item['id']:item for item in items}
    first={rid:[item['updated']] for rid,item in by_id.items()}
    latest={rid:[item['updated']] for rid,item in by_id.items()}
    marks=','.join('?' for _ in by_id)
    for row in db.execute('SELECT record_id,payload FROM asset_events WHERE action="record_before_update" AND record_id IN ('+marks+')',list(by_id)):
        previous=json.loads(row['payload']).get('updated')
        if previous:first[row['record_id']].append(previous)
    for row in db.execute('SELECT record_id,min(created) AS first,max(created) AS last FROM asset_document_links WHERE record_id IN ('+marks+') GROUP BY record_id',list(by_id)):
        first[row['record_id']].append(row['first']);latest[row['record_id']].append(row['last'])
    for rid,item in by_id.items():
        item['storedAt']=min(first[rid]);item['lastStoredAt']=max(latest[rid])

def product_ui_eligible(metadata, kind):
    return (kind in PRODUCT_UI_KINDS and metadata.get('evidenceRole') == 'product_ui_original'
            and all(str(metadata.get(field) or '').strip() for field in ('productName', 'sourceProvenance', 'inspectionScope')))

def search(db,query='',kind='',category='',limit=30,offset=0,sort='default',include_context=False,scope='all',subtype='',tag=''):
    # Literal substrings work for Chinese, including two-character terms. No query text becomes SQL.
    tokens=[t.lower() for t in re.split(r'\s+',query.strip()) if t][:12]
    where=['r.id NOT IN (SELECT alias FROM asset_aliases)', 'r.id NOT IN (' + asset_exclusion.SQL + 'SELECT id FROM blocked)'];args=[]
    if scope == 'product-ui':
        if include_context:raise ValueError('product-ui 检索不能包含上下文证据')
        where.append("r.kind IN ('image','reference_image','video','reference_video')")
        where.append("json_extract(r.metadata,'$.evidenceRole')='product_ui_original'")
        for field in ('productName','sourceProvenance','inspectionScope'):
            where.append(f"length(trim(coalesce(json_extract(r.metadata,'$.{field}'),'')))>0")
    elif scope == 'all' and not include_context:
        where.append("coalesce(json_extract(r.metadata,'$.evidenceRole'),'') NOT IN ('feedback_context','conversation_context','production_context')")
    elif scope != 'all':raise ValueError('invalid search scope')
    if kind:where.append('r.kind=?');args.append(kind)
    if category:where.append('r.category=?');args.append(category)
    if subtype:where.append("json_extract(r.metadata,'$.classification.subtype')=?");args.append(subtype)
    if tag:where.append("EXISTS(SELECT 1 FROM json_each(r.metadata,'$.classification.tags') WHERE value=?)");args.append(tag)
    for t in tokens:
        where.append('''(instr(lower(r.title||' '||r.category||' '||r.metadata),?)>0 OR EXISTS(SELECT 1 FROM asset_document_links l JOIN asset_documents d ON d.sha=l.sha WHERE l.record_id=r.id AND instr(lower(d.body),?)>0))''');args.extend([t,t])
    clause=' AND '.join(where)
    count=db.execute('SELECT count(*) FROM asset_records r WHERE '+clause,args).fetchone()[0]
    if sort not in {'default','stored_desc','stored_asc'}:raise ValueError('invalid sort')
    prefix='';joins=''
    order='CASE r.kind WHEN "reference_video" THEN 0 WHEN "analysis_document" THEN 1 WHEN "frame_evidence" THEN 9 ELSE 2 END,r.title,r.id'
    if sort!='default':
        prefix="WITH history AS (SELECT record_id,min(json_extract(payload,'$.updated')) AS first FROM asset_events WHERE action='record_before_update' GROUP BY record_id), docs AS (SELECT record_id,min(created) AS first FROM asset_document_links GROUP BY record_id) "
        joins=' LEFT JOIN history h ON h.record_id=r.id LEFT JOIN docs d ON d.record_id=r.id '
        order='min(r.updated,coalesce(h.first,r.updated),coalesce(d.first,r.updated)) '+('DESC' if sort=='stored_desc' else 'ASC')+',r.id'
    rows=db.execute(prefix+'SELECT r.* FROM asset_records r'+joins+' WHERE '+clause+' ORDER BY '+order+' LIMIT ? OFFSET ?',args+[min(max(limit,1),100),max(offset,0)]).fetchall()
    items=[dict(r) for r in rows]
    for r in items:r['metadata']=json.loads(r['metadata'])
    attach_storage_times(db,items)
    return {'items':items,'count':count,'offset':offset,'limit':limit}

def backfill_classification(db,apply=False):
    rows=db.execute('SELECT * FROM asset_records WHERE id NOT IN (SELECT alias FROM asset_aliases)').fetchall()
    db.execute('SAVEPOINT classification_backfill')
    before=db.total_changes
    for r in rows:record(db,r['id'],r['title'],r['kind'],json.loads(r['metadata']),r['platform'],legacy=r['legacy_id'])
    result={'mode':'applied' if apply else 'preview','sqlChanges':db.total_changes-before,**stats(db)}
    if apply:db.execute('RELEASE classification_backfill');db.commit()
    else:db.execute('ROLLBACK TO classification_backfill');db.execute('RELEASE classification_backfill')
    return result

def lookup(db,path=None,url=None):
    sha=digest(path) if path else None
    if sha: ids=[r[0] for r in db.execute('SELECT DISTINCT record_id FROM asset_links WHERE sha=?',(sha,))]
    elif url:ids=[r[0] for r in db.execute('SELECT record_id FROM asset_sources WHERE uri=?',(normalize_url(url),))]
    else:raise ValueError('lookup 需要 --file 或 --url')
    visible=[]
    for rid in ids:
        try:
            item=detail(db,rid,False)
            if item['id'] not in {x['id'] for x in visible}:visible.append(item)
        except ValueError:
            continue
    return {'match':'exact_bytes' if sha and visible else 'same_source_candidate' if visible else 'excluded' if ids else 'none','sha256':sha,'records':visible,'note':'相同发布地址可能包含多个视频；只有文件哈希一致才能判定同一原件。已有分析不代表已全部复核。'}

def detail(db,rid,with_body=True):
    if asset_exclusion.blocked(db,rid):raise ValueError('资产已排除，不允许通过此入口取用')
    alias=db.execute('SELECT record_id FROM asset_aliases WHERE alias=?',(rid,)).fetchone()
    if alias:rid=alias[0]
    row=db.execute('SELECT * FROM asset_records WHERE id=?',(rid,)).fetchone()
    if not row:raise KeyError(rid)
    data=dict(row);data['metadata']=json.loads(data['metadata'])
    attach_storage_times(db,[data])
    if data['metadata'].get('retrievalExcluded'):raise ValueError('资产已排除，不允许通过此入口取用')
    data['resultHeads']=asset_results.heads(db,rid)
    data['objects']=[dict(r) for r in db.execute('SELECT o.*,l.role FROM asset_links l JOIN asset_objects o ON o.sha=l.sha WHERE l.record_id=?',(rid,))]
    for obj in data['objects']:
        obj['locations']=[dict(r) for r in db.execute('SELECT path,verified FROM asset_locations WHERE sha=?',(obj['sha'],))]
        obj['cloudVerified']=bool(db.execute('SELECT 1 FROM asset_cloud_receipts WHERE sha=?',(obj['sha'],)).fetchone())
    data['documents']=[dict(r) for r in db.execute('SELECT l.path,l.sha,l.created,d.format'+(',d.body' if with_body else '')+' FROM asset_document_links l JOIN asset_documents d ON d.sha=l.sha WHERE l.record_id=? ORDER BY l.created DESC',(rid,))]
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='asset_document_sections'").fetchone():
        data['documentSections']=[dict(r) for r in db.execute('SELECT * FROM asset_document_sections WHERE record_id=?',(rid,))]
    data['sources']=[r[0] for r in db.execute('SELECT uri FROM asset_sources WHERE record_id=?',(rid,))]
    if row['legacy_id']:
        legacy=db.execute('SELECT i.review_status,i.rights_status,i.ai_status,v.payload_json FROM library_items i LEFT JOIN library_item_versions v ON i.current_version_id=v.version_id WHERE i.item_id=?',(row['legacy_id'],)).fetchone()
        data['workbench']=dict(legacy) if legacy else None
    return data

def duplicates(db):
    rows=db.execute('SELECT o.sha,o.size,count(*) paths FROM asset_objects o JOIN asset_locations l ON l.sha=o.sha GROUP BY o.sha HAVING count(*)>1 ORDER BY o.size DESC').fetchall()
    result=[]
    for row in rows:
        locations=[dict(r) for r in db.execute('SELECT * FROM asset_locations WHERE sha=?',(row['sha'],))]
        unique=len({(r['device'],r['inode']) for r in locations})
        result.append({**dict(row),'locations':locations,'logicalDuplicateBytes':max(0,unique-1)*row['size'],'cleanupStatus':'blocked_until_cloud_and_dependency_verification'})
    return {'groups':result,'count':len(result),'logicalDuplicateBytes':sum(r['logicalDuplicateBytes'] for r in result),'deleted':0}

def backup(db,target):
    p=Path(target);p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():raise ValueError('备份目标已存在，不能覆盖历史备份')
    dest=sqlite3.connect(p)
    try:
        db.backup(dest)
        if dest.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('备份完整性检查失败')
    finally:dest.close()
    p.chmod(0o600);return {'path':str(p),'sha256':digest(p),'bytes':p.stat().st_size}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--db',required=True)
    sub=ap.add_subparsers(dest='command',required=True)
    sub.add_parser('init');sub.add_parser('stats');sub.add_parser('duplicates');sub.add_parser('sync-workbench')
    sub.add_parser('init-results')
    p=sub.add_parser('classify-history');p.add_argument('--apply',action='store_true')
    p=sub.add_parser('import-summaries');p.add_argument('root');p.add_argument('--apply',action='store_true')
    p=sub.add_parser('import-projects');p.add_argument('root')
    p=sub.add_parser('import-inventory');p.add_argument('path')
    p=sub.add_parser('scan');p.add_argument('root')
    p=sub.add_parser('search');p.add_argument('query',nargs='?',default='');p.add_argument('--kind',default='');p.add_argument('--category',default='');p.add_argument('--subtype',default='');p.add_argument('--tag',default='');p.add_argument('--limit',type=int,default=30);p.add_argument('--offset',type=int,default=0);p.add_argument('--sort',choices=['default','stored_desc','stored_asc'],default='default');p.add_argument('--include-context',action='store_true');p.add_argument('--scope',choices=['all','product-ui'],default='all')
    p=sub.add_parser('lookup');g=p.add_mutually_exclusive_group(required=True);g.add_argument('--file');g.add_argument('--url')
    p=sub.add_parser('get');p.add_argument('id');p.add_argument('--scope',choices=['all','product-ui'],default='all')
    p=sub.add_parser('submit');p.add_argument('--request',required=True)
    p=sub.add_parser('compat-video-flow');p.add_argument('--request',required=True)
    p=sub.add_parser('retry');p.add_argument('request_id')
    sub.add_parser('pending')
    sub.add_parser('workflow-catalog')
    p=sub.add_parser('usage');g=p.add_mutually_exclusive_group(required=True);g.add_argument('--project');g.add_argument('--project-root')
    p=sub.add_parser('submit-usage');p.add_argument('--request',required=True)
    p=sub.add_parser('read-result');p.add_argument('id');p.add_argument('--producer',required=True);p.add_argument('--stream',required=True);p.add_argument('--version')
    p=sub.add_parser('backup');p.add_argument('target')
    p=sub.add_parser('register');p.add_argument('--file',required=True);p.add_argument('--title');p.add_argument('--kind',default='reference_video');p.add_argument('--category',default='');p.add_argument('--batch-category',default='');p.add_argument('--platform',default='');p.add_argument('--url');p.add_argument('--analysis',action='append',default=[]);p.add_argument('--classification-file');p.add_argument('--legacy-id');p.add_argument('--evidence-role',choices=sorted(EVIDENCE_ROLES));p.add_argument('--product-name');p.add_argument('--source-provenance');p.add_argument('--inspection-scope')
    args=ap.parse_args();write=args.command in {'init','init-results','import-summaries','import-inventory','scan','register','sync-workbench','import-projects','classify-history'}
    if args.command in {'submit','retry','pending','compat-video-flow','submit-usage'}:
        if args.command=='pending':result=asset_results.pending(args.db)
        elif args.command=='retry':result=asset_results.submit(args.db,sys.modules[__name__],retry_id=args.request_id)
        else:
            request=json.load(sys.stdin) if args.request=='-' else json.loads(Path(args.request).read_text())
            result=asset_usage.submit(args.db,request,sys.modules[__name__]) if args.command=='submit-usage' else asset_compat.run(args.db,request['command'],request['options'],sys.modules[__name__]) if args.command=='compat-video-flow' else asset_results.submit(args.db,sys.modules[__name__],request=request)
        print(dumps(result))
        if result.get('state')=='pending_retry':raise SystemExit(2)
        return
    if args.command=='init' and not Path(args.db).exists():Path(args.db).parent.mkdir(parents=True,exist_ok=True);sqlite3.connect(args.db).close()
    with contextlib.closing(connect(args.db,write)) as db:
        if write:init(db)
        c=args.command
        if c in ('init','stats'):result=stats(db)
        elif c=='init-results':asset_results.init(db);result={'state':'ready','resultProtocolVersion':1}
        elif c=='classify-history':result=backfill_classification(db,args.apply)
        elif c=='import-summaries':result=import_summaries(db,args.root,apply=args.apply,catalog=sys.modules[__name__])
        elif c=='import-inventory':result=import_inventory(db,args.path)
        elif c=='scan':result=scan(db,args.root)
        elif c=='sync-workbench':result=sync_workbench(db)
        elif c=='import-projects':result=project_manifests(db,args.root)
        elif c=='workflow-catalog':result=asset_workflow_catalog.read(db)
        elif c=='usage':result=asset_usage.read(db,args.project or 'local-project:'+key(str(Path(args.project_root).resolve()))[:24])
        elif c=='search':result=search(db,args.query,args.kind,args.category,args.limit,args.offset,args.sort,args.include_context,args.scope,args.subtype,args.tag)
        elif c=='lookup':result=lookup(db,args.file,args.url)
        elif c=='get':
            result=detail(db,args.id)
            if args.scope=='product-ui' and not product_ui_eligible(result['metadata'],result['kind']):
                raise ValueError('该资产未经核实，不能作为产品 UI 复刻依据')
        elif c=='read-result':result=asset_results.read(db,args.id,args.producer,args.stream,args.version)
        elif c=='duplicates':result=duplicates(db)
        elif c=='backup':result=backup(db,args.target)
        elif c=='register':
            with db:
                classification_override=read_classification(args.classification_file) if args.classification_file else None
                if args.evidence_role=='product_ui_original':
                    if args.kind not in PRODUCT_UI_KINDS:raise ValueError('产品 UI 原片必须是图片或视频')
                    if not all((x or '').strip() for x in (args.product_name,args.source_provenance,args.inspection_scope)):
                        raise ValueError('产品 UI 原片须提供产品名、来源依据和实际检查范围')
                elif any((x or '').strip() for x in (args.product_name,args.source_provenance,args.inspection_scope)):
                    raise ValueError('产品来源字段只能与 --evidence-role product_ui_original 一同提交')
                if args.legacy_id and not db.execute("SELECT 1 FROM library_items WHERE item_id=? AND entity_kind='reference_video'",(args.legacy_id,)).fetchone():raise ValueError('工作台参考 ID 不存在')
                sha=register_file(db,args.file)
                if not sha:raise ValueError('文件不存在或读取期间发生变化')
                if db.execute(asset_exclusion.SQL + "SELECT 1 FROM asset_links l JOIN blocked b ON b.id=l.record_id WHERE l.sha=?",(sha,)).fetchone():raise ValueError('文件对应已排除资产，不允许重新登记启用')
                existing=db.execute('SELECT r.id FROM asset_links l JOIN asset_records r ON r.id=l.record_id WHERE l.sha=? AND r.kind=? ORDER BY r.id LIMIT 1',(sha,args.kind)).fetchone()
                rid=existing['id'] if existing else 'asset:'+sha
                collision=db.execute('SELECT kind FROM asset_records WHERE id=?',(rid,)).fetchone()
                if collision and collision['kind']!=args.kind:rid='asset:'+key(args.kind+':'+sha)
                old=db.execute('SELECT * FROM asset_records WHERE id=?',(rid,)).fetchone()
                metadata=json.loads(old['metadata']) if old else {'reviewStatus':'pending'}
                metadata.setdefault('sourceFilename',Path(args.file).name)
                if args.evidence_role:
                    metadata['evidenceRole']=args.evidence_role
                    metadata['evidenceRoleBasis']='explicit registration'
                elif args.kind in PRODUCT_UI_KINDS:
                    metadata.setdefault('evidenceRole','unverified')
                if args.evidence_role=='product_ui_original':
                    metadata.update(productName=args.product_name.strip(),sourceProvenance=args.source_provenance.strip(),inspectionScope=args.inspection_scope.strip())
                record(db,rid,args.title or (old['title'] if old else Path(args.file).stem),args.kind,metadata,args.platform or (old['platform'] if old else ''),args.category,args.batch_category,args.legacy_id or (old['legacy_id'] if old else None),classification_override)
                if args.legacy_id:
                    db.execute('INSERT OR REPLACE INTO asset_legacy_links VALUES(?,?)',(args.legacy_id,rid))
                    alias='legacy:'+args.legacy_id
                    if alias!=rid and db.execute('SELECT 1 FROM asset_records WHERE id=?',(alias,)).fetchone():db.execute('INSERT OR REPLACE INTO asset_aliases VALUES(?,?)',(alias,rid))
                db.execute('INSERT OR IGNORE INTO asset_links VALUES(?,?,?)',(rid,sha,'source'))
                if args.url:db.execute('INSERT OR IGNORE INTO asset_sources VALUES(?,?)',(rid,normalize_url(args.url)))
                for p in args.analysis:document(db,rid,p)
            result=detail(db,rid,False)
        print(dumps(result))
if __name__=='__main__':
    try:main()
    except Exception as e:print(dumps({'error':str(e),'type':type(e).__name__}),file=sys.stderr);sys.exit(1)
