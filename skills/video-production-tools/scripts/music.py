"""Automatic music selection from the user's library, with actual file/evidence hashes."""
import argparse,json,hashlib,subprocess,sys
from pathlib import Path
from runtime import library,ref

def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
 a=sub.add_parser('add');a.add_argument('--file',required=True);a.add_argument('--title',required=True);a.add_argument('--license-file',required=True);a.add_argument('--rights',choices=['owned','licensed','generated'],required=True);a.add_argument('--source-url',required=True);a.add_argument('--tags',nargs='*',default=[])
 a=sub.add_parser('plan');a.add_argument('--query',required=True);a.add_argument('--seconds',type=float,required=True);a.add_argument('--out',required=True)
 a=sub.add_parser('apply');a.add_argument('--project',type=Path,required=True);a.add_argument('--selection',type=Path,required=True)
 a=sub.add_parser('cost');a.add_argument('--manifest',required=True);a.add_argument('--prices',required=True)
 a=p.parse_args()
 if a.cmd=='cost':
  m=json.loads(Path(a.manifest).read_text());prices=json.loads(Path(a.prices).read_text());items=[]
  for x in m.get('generated',[]):
   rate=prices.get(x['provider'],{}).get('perSecond');items.append({'requestHash':x['request_hash'],'cacheHit':x['cache_hit'],'newAudioSeconds':0 if x['cache_hit'] else x['quality']['duration_seconds'],'estimatedCost':0 if x['cache_hit'] else x['quality']['duration_seconds']*rate if isinstance(rate,(int,float)) else None,'pricingBasis':prices.get(x['provider'],{}),'finalBill':'supplier_bill_not_checked'})
  return {'items':items,'meaning':'perSecond is a user supplied budgeting rate, not a claim about provider actual billing; missing rate is unknown, not free'}
 if a.cmd=='apply':
  selection=json.loads(a.selection.read_text());chosen=selection['selected'];file=Path(chosen['path']);e=Path(chosen['licenseEvidence'])
  if ref.digest(file)!=chosen['sha256'] or ref.digest(e)!=chosen['licenseSha256']:raise ValueError('音乐或许可证据已变化')
  project=a.project.resolve();plan=json.loads((project/'workflow/plan.json').read_text());total=sum(x['duration'] for x in plan['shots'])
  if abs(total-selection['duration'])>.001:raise ValueError('选曲方案与当前分镜时长不符')
  aid='bgm-'+chosen['sha256'][:16];ledger=json.loads((project/'workflow/assets.json').read_text());old=next((x for x in ledger['assets'] if x['id']==aid),None)
  if old and old['sha256']!=chosen['sha256']:raise ValueError('已有音乐身份冲突')
  if not old:
   cli=Path(__file__).resolve().parents[3]/'video_make.py';subprocess.run([sys.executable,str(cli),'add-asset','--project',str(project),'--id',aid,'--file',str(file),'--kind','audio','--origin','user_provided','--source',chosen['sourceUrl'],'--rights',chosen['rightsStatus'],'--basis','用户库中记录的许可或自有依据SHA256:'+chosen['licenseSha256']],check=True,capture_output=True)
  proof=project/'workflow/license-evidence'/e.name;proof.parent.mkdir(parents=True,exist_ok=True)
  if proof.exists() and ref.digest(proof)!=chosen['licenseSha256']:raise ValueError('项目内许可证据冲突')
  if not proof.exists():proof.write_bytes(e.read_bytes())
  tracks=plan['audio'].get('tracks',[])
  if any(x.get('role')=='bgm' for x in tracks):raise ValueError('已有BGM，须先处理替换范围，不能叠加两首')
  tracks.append({'asset':aid,'role':'bgm','at':0,'in':0,'duration':total,'gainDb':selection['gainDb'],'fadeIn':min(selection['fadeIn'],total/2),'fadeOut':min(selection['fadeOut'],total/2)})
  plan['audio']={'mode':'mix','reason':'旁白优先；来自已核对文件与许可证据的用户音乐库，固定增益与首尾淡入淡出','tracks':tracks};ref.write(project/'workflow/plan.json',plan)
  return {'state':'music_plan_attached_not_yet_mixed','assetId':aid,'next':'run video_make validate/render/check; listen to actual output'}
 lib=library()
 if a.cmd=='add':
  if not lib.root:raise ValueError('统一生产库请沿用既有声音登记入口；此命令用于自己的便携库')
  src=Path(a.file).resolve();evidence=Path(a.license_file).resolve();sha=ref.digest(evidence);dest=lib.root/'license-evidence'/f'{sha}.txt';dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():dest.write_bytes(evidence.read_bytes())
  info={'licenseEvidence':str(dest.relative_to(lib.root)),'licenseSha256':sha,'sourceUrl':a.source_url,'tags':a.tags,'licenseReview':'recorded_user_declaration_not_independent_legal_verification'}
  annotation=lib.root/'license-evidence'/f'{sha}.json';annotation.write_text(json.dumps(info,ensure_ascii=False))
  cli=Path(__file__).resolve().parents[3]/'video_library.py'
  cmd=[sys.executable,str(cli),'--library',str(lib.root),'ingest','--file',str(src),'--title',a.title,'--kind','music_track','--category','背景音乐','--rights',a.rights,'--rights-basis',f'许可或自有依据文件SHA256:{sha}','--analysis',str(annotation),'--tags',*a.tags]
  r=subprocess.run(cmd,text=True,capture_output=True,check=True);return json.loads(r.stdout)
 if not 0<a.seconds<=1800:raise ValueError('时长须在0至1800秒之间')
 choices=[]
 def rows():
  offset=0
  while True:
   page=lib.call('search','','--kind','music_track','--limit','100','--offset',str(offset))
   yield from page['items'];offset+=len(page['items'])
   if not page['items'] or offset>=page['count']:break
   if offset>10000:raise ValueError('曲库超过本次检索上限，需按用途缩小范围')
 for row in rows():
  item=lib.call('get',row['id']);head=next((h for h in item['resultHeads'] if h['producer']=='video-asset-library' and h['stream']=='catalog-notes'),None)
  if not head:continue
  body=json.loads(lib.call('read-result',row['id'],'--producer','video-asset-library','--stream','catalog-notes')['payload']['documents'][0]['body'])
  if body['rights']['status'] not in ['owned','licensed','generated']:continue
  try:meta=json.loads(body['analysis']);e=lib.root/meta['licenseEvidence'] if lib.root else None
  except (TypeError,ValueError,KeyError):continue
  if not e or not e.is_file() or ref.digest(e)!=meta['licenseSha256']:continue
  candidates=[(p,obj['sha']) for obj in item['objects'] for p in ((list((lib.root/'objects'/obj['sha']).glob('source.*')) if lib.root else [])+[Path(loc['path']) for loc in obj['locations']])]
  file=next((p for p,sha in candidates if p.is_file() and ref.digest(p)==sha),None)
  if not file:continue
  probe=json.loads(ref.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',file]));duration=float(probe['format']['duration'])
  if not any(s['codec_type']=='audio' for s in probe['streams']) or duration<a.seconds:continue
  score=sum(t.lower() in (item['title']+' '+str(body['tags'])+' '+body['use']).lower() for t in a.query.split())
  choices.append({'assetId':item['id'],'path':str(file),'sha256':ref.digest(file),'licenseEvidence':str(e),'licenseSha256':meta['licenseSha256'],'rightsStatus':body['rights']['status'],'score':score,'sourceUrl':meta['sourceUrl']})
 if not choices:raise ValueError('没有足长且文件/许可证据通过核对的音乐；先取得用户自己的可用曲目，不伪造保底文件')
 choices.sort(key=lambda x:(-x['score'],x['assetId']));result={'status':'selected_not_mixed','selected':choices[0],'reason':'literal_tag_match' if choices[0]['score'] else 'available_fallback_no_style_match','duration':a.seconds,'gainDb':-22,'fadeIn':.5,'fadeOut':1,'at':0,'loop':False,'listening':'pending','rights':'evidence hashes checked; user rights declaration still requires actual review'}
 if Path(a.out).exists():raise ValueError('不覆盖旧选曲计划')
 ref.write(a.out,result);return result
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1] in ['generate','configure-key']:
  raise SystemExit(subprocess.call([sys.executable,str(Path(__file__).with_name('music_google.py')),*sys.argv[1:]]))
 try:print(json.dumps(main(),ensure_ascii=False,indent=2))
 except Exception as e:print(json.dumps({'status':'failed','error':str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(1)
