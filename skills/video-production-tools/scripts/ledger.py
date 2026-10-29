"""Append-only production decisions, snapshots, revision guards and actual decoded comparisons."""
import argparse,json,hashlib,datetime,uuid,subprocess,shutil
from pathlib import Path
from runtime import ref

def main():
 p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);sub=p.add_subparsers(dest='cmd',required=True)
 sub.add_parser('init');sub.add_parser('status');sub.add_parser('snapshot')
 a=sub.add_parser('decision');a.add_argument('--file',required=True);a.add_argument('--status',choices=['approved','rejected','superseded'],required=True);a.add_argument('--by',required=True);a.add_argument('--evidence',required=True);a.add_argument('--scope',required=True);a.add_argument('--reason',required=True)
 a=sub.add_parser('rollback');a.add_argument('--snapshot',required=True)
 a=sub.add_parser('protect');a.add_argument('--shots',nargs='+',required=True);a.add_argument('--baseline',required=True);a.add_argument('--evidence',required=True)
 a=sub.add_parser('verify');a.add_argument('--candidate',required=True)
 a=p.parse_args();root=a.project.resolve();folder=root/'production-ledger';path=folder/'ledger.json'
 def local(name):
  q=(root/name).resolve()
  if not q.is_relative_to(root) or not q.is_file():raise ValueError('文件缺失或越出项目：'+str(name))
  return q
 def save(data):ref.write(path,data)
 def read():return json.loads(path.read_text())
 def event(data,kind,**fields):data['events'].append({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'type':kind,**fields});save(data)
 if a.cmd=='init':
  if path.exists():raise ValueError('已有账本，不覆盖')
  save({'schemaVersion':1,'events':[],'decisions':[],'headSnapshot':None});return {'state':'initialized','userApproved':False}
 data=read()
 if a.cmd=='status':return data
 if a.cmd=='snapshot':
  ident=uuid.uuid4().hex;dest=folder/'snapshots'/ident;dest.mkdir(parents=True);files={}
  for name in ['workflow/plan.json','workflow/assets.json','workflow/script.locked.txt','workflow/visual-reference-contract.json']:
   if (root/name).is_file():
    content=local(name).read_bytes();q=dest/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(content);files[name]=ref.digest(q)
  ref.write(dest/'snapshot.json',{'files':files});data['headSnapshot']=ident;event(data,'snapshot',snapshot=ident);return {'snapshot':ident,'files':files}
 if a.cmd=='decision':
  file=local(a.file);e=local(a.evidence)
  if not all([a.by.strip(),a.scope.strip(),a.reason.strip(),e.read_text().strip()]):raise ValueError('缺少主体、范围、原因或证据')
  item={'file':a.file,'sha256':ref.digest(file),'status':a.status,'by':a.by,'scope':a.scope,'reason':a.reason,'evidence':a.evidence,'evidenceSha256':ref.digest(e),'authority':'recorded assertion; tool cannot authenticate human author'}
  data['decisions'].append(item);event(data,'decision',decision=item);return item
 if a.cmd=='rollback':
  if not a.snapshot.isalnum():raise ValueError('快照ID无效')
  dest=folder/'snapshots'/a.snapshot;meta=json.loads((dest/'snapshot.json').read_text())
  for name,sha in meta['files'].items():
   source=(dest/name).resolve();target=(root/name).resolve()
   if not source.is_relative_to(dest.resolve()) or not target.is_relative_to(root) or ref.digest(source)!=sha:raise ValueError('快照身份或路径不符')
  # Save current state before restoring; media and candidates are never deleted.
  backup=folder/'before-rollback'/uuid.uuid4().hex
  for name in meta['files']:
   if (root/name).is_file():q=backup/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,q)
   q=root/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(dest/name,q)
  data['headSnapshot']=a.snapshot;event(data,'rollback',snapshot=a.snapshot,previousState=str(backup.relative_to(root)));return {'restored':list(meta['files']),'mediaDeleted':False}
 plan=json.loads(local('workflow/plan.json').read_text());assets=json.loads(local('workflow/assets.json').read_text())
 if a.cmd=='protect':
  e=local(a.evidence);baseline=local(a.baseline)
  if not set(a.shots)<=set(s['id'] for s in plan['shots']):raise ValueError('修改镜头ID不在分镜内')
  guard={'plan':plan,'assets':assets,'changedShots':a.shots,'baseline':a.baseline,'baselineSha256':ref.digest(baseline),'evidence':a.evidence,'evidenceSha256':ref.digest(e)};ref.write(folder/'revision-guard.json',guard);event(data,'revision_contract',shots=a.shots);return {'protected':True,'baselineSha256':guard['baselineSha256']}
 guard=json.loads((folder/'revision-guard.json').read_text());baseline=local(guard['baseline']);candidate=local(a.candidate)
 if ref.digest(baseline)!=guard['baselineSha256']:raise ValueError('基线视频变化')
 if ref.digest(local(guard['evidence']))!=guard['evidenceSha256']:raise ValueError('修改依据变化')
 old=guard['plan'];errors=[]
 for file in [baseline,candidate]:
  meta=json.loads(ref.run(['ffprobe','-v','error','-show_format','-of','json',file]))
  if abs(float(meta['format']['duration'])-sum(x['duration'] for x in old['shots']))>.06:errors.append('实际视频时长与基线分镜不符')
 if old['audio']!=plan['audio'] or old['canvas']!=plan['canvas'] or old['scriptSha256']!=plan['scriptSha256']:errors.append('声音、画幅或锁稿发生范围外变化')
 if [s['id'] for s in old['shots']]!=[s['id'] for s in plan['shots']]:errors.append('镜头顺序或数量变化')
 oldassets={x['id']:x for x in guard['assets']['assets']};newassets={x['id']:x for x in assets['assets']}
 for x in newassets.values():
  if ref.digest(local(x['path']))!=x['sha256']:errors.append('素材身份变化：'+x['id'])
 start=0;protected=[]
 for before,after in zip(old['shots'],plan['shots']):
  if before['duration']!=after['duration']:errors.append('时长变化：'+before['id'])
  if before['id'] not in guard['changedShots']:
   if before!=after:errors.append('未标镜头分镜变化：'+before['id'])
   for asset in [before['asset'],*[x['asset'] for x in before.get('layers',[])]]:
    if oldassets[asset]!=newassets.get(asset):errors.append('未标镜头素材变化：'+asset)
   def frames(file):
    raw=ref.run(['ffmpeg','-v','error','-ss',str(start),'-i',file,'-t',str(before['duration']),'-an','-f','framemd5','-'])
    return [l.rsplit(',',1)[-1].strip() for l in raw.splitlines() if l and not l.startswith('#')]
   if frames(baseline)!=frames(candidate):errors.append('未标镜头实际解码画面变化：'+before['id'])
   protected.append(before['id'])
  start+=before['duration']
 for track in old['audio']['tracks']:
  if oldassets[track['asset']]!=newassets.get(track['asset']):errors.append('音源身份变化')
 def audio(file):return subprocess.run(['ffmpeg','-v','error','-i',str(file),'-vn','-c:a','pcm_s16le','-f','hash','-'],capture_output=True,text=True)
 one,two=audio(baseline),audio(candidate)
 if (one.returncode==0)!=(two.returncode==0) or one.stdout!=two.stdout:errors.append('实际解码音轨变化')
 # Reject an exact byte version the user already rejected.
 if any(d['sha256']==ref.digest(candidate) and d['status']=='rejected' for d in data['decisions']):errors.append('候选仍为已拒收版本')
 result={'passed':not errors,'errors':errors,'protectedShots':protected,'baselineSha256':guard['baselineSha256'],'candidateSha256':ref.digest(candidate),'aesthetic':'not_judged'};ref.write(folder/'revision-check.json',result)
 if errors:raise ValueError(json.dumps(result,ensure_ascii=False))
 event(data,'revision_verified',result=result);return result
if __name__=='__main__':
 try:print(json.dumps(main(),ensure_ascii=False,indent=2))
 except Exception as e:print(json.dumps({'state':'failed','error':str(e)},ensure_ascii=False),file=__import__('sys').stderr);raise SystemExit(1)
