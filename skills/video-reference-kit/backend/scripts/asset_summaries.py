"""Import historical compilations without creating duplicate video records."""
import csv, hashlib, json, re
from pathlib import Path

def import_summaries(db, root, *, apply, catalog):
    root=Path(root).resolve()
    paths=[root/'抖音短视频黄金三秒汇总.md',root/'抖音短视频黄金三秒汇总.csv',root/'项目参考视频分镜总表.md']
    for p in paths:
        if not p.is_file(): raise ValueError(f'专项总结缺失：{p}')
    db.execute('SAVEPOINT summaries_import')
    before=db.total_changes
    report={'mode':'applied' if apply else 'preview','sources':[],'linkedSections':0,'unmatched':[],'newVideoRecords':0}
    try:
        docs={}
        for p in paths:
            rid='doc:'+catalog.key(str(p))
            old=db.execute('SELECT metadata FROM asset_records WHERE id=?',(rid,)).fetchone()
            meta=json.loads(old[0]) if old else {'sourcePath':str(p),'reviewStatus':'historical_unreviewed','scope':'historical_compilation','note':'原文迁移，不构成重新听辨、原始转写核验或批准'}
            catalog.record(db,rid,p.stem,'analysis_document',meta)
            catalog.document(db,rid,p)
            sha=catalog.digest(p);docs[p.name]=(rid,sha,p.read_text(encoding='utf-8'))
            report['sources'].append({'path':str(p),'recordId':rid,'sha256':sha,'bytes':p.stat().st_size})
        def attach(rid,p,start,end,label):
            source_sha=docs[p.name][1]
            body=''.join(p.read_text(encoding='utf-8').splitlines(keepends=True)[start-1:end])
            sha=hashlib.sha256(body.encode('utf-8')).hexdigest()
            locator=f'{p}#L{start}-L{end}'
            db.execute('INSERT OR IGNORE INTO asset_documents VALUES(?,?,?)',(sha,body,p.suffix))
            db.execute('INSERT OR IGNORE INTO asset_document_links VALUES(?,?,?,?)',(rid,locator,sha,catalog.STAMP()))
            db.execute('INSERT OR IGNORE INTO asset_document_sections VALUES(?,?,?,?,?,?,?)',(rid,source_sha,sha,str(p),start,end,label))
            report['linkedSections']+=1
        def resolve_id(video_id):
            rows=db.execute("SELECT id FROM asset_records WHERE kind='reference_video' AND id=?",('ref:dy:'+video_id,)).fetchall()
            return [r[0] for r in rows]
        # Keep the Markdown section exact, including original uncertainty and ASR coverage.
        p=paths[0];lines=docs[p.name][2].splitlines(keepends=True)
        starts=[i for i,line in enumerate(lines) if re.match(r'^### \d+\.',line)]
        md_ids=[]
        for i in starts:
            end=next((j for j in range(i+1,len(lines)) if re.match(r'^#{1,3} ',lines[j])),len(lines))
            section=''.join(lines[i:end]);match=re.search(r'抖音 ID：`(\d+)`',section)
            if not match: report['unmatched'].append({'file':p.name,'line':i+1,'reason':'missing_video_id'});continue
            vid=match.group(1);md_ids.append(vid);ids=resolve_id(vid)
            if len(ids)!=1:report['unmatched'].append({'videoId':vid,'candidates':ids});continue
            attach(ids[0],p,i+1,end,lines[i].strip())
        with paths[1].open(encoding='utf-8-sig',newline='') as stream:
            csv_ids=[r['抖音ID'] for r in csv.DictReader(stream)]
        if sorted(csv_ids)!=sorted(md_ids):raise ValueError('Markdown 与 CSV 的视频 ID 集合不一致，需先核对')
        if len(md_ids)!=len(set(md_ids)):raise ValueError('Markdown 包含重复视频 ID')
        report['golden3Rows']=len(md_ids)
        # Resolve the eight inventory entries using actual file hashes, never fuzzy titles.
        p=paths[2];text=docs[p.name][2];lines=text.splitlines(keepends=True)
        sources={}
        for line in lines:
            m=re.match(r'^\| (\d\d) \| [^|]+ \| `([^`]+)`',line)
            if m:sources[m[1]]=m[2]
        for i,line in enumerate(lines):
            m=re.match(r'^## (\d\d)\. ',line)
            if not m:continue
            end=next((j for j in range(i+1,len(lines)) if lines[j].startswith('## ')),len(lines))
            source=root/sources.get(m[1],'__missing__')
            if not source.is_file():report['unmatched'].append({'section':line.strip(),'source':str(source),'reason':'missing_source'});continue
            sha=catalog.digest(source)
            rows=db.execute("SELECT DISTINCT r.id FROM asset_links l JOIN asset_records r ON r.id=l.record_id WHERE l.sha=? AND r.kind='reference_video' AND r.id NOT IN (SELECT alias FROM asset_aliases)",(sha,)).fetchall()
            ids=[r[0] for r in rows]
            if len(ids)!=1:report['unmatched'].append({'section':line.strip(),'sourceSha256':sha,'candidates':ids});continue
            attach(ids[0],p,i+1,end,line.strip())
        report['sqlChanges']=db.total_changes-before
        if apply:db.execute('RELEASE summaries_import');db.commit()
        else:db.execute('ROLLBACK TO summaries_import');db.execute('RELEASE summaries_import')
        return report
    except Exception:
        db.execute('ROLLBACK TO summaries_import');db.execute('RELEASE summaries_import');raise
