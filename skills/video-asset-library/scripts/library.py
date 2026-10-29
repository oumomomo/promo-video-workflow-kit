#!/usr/bin/env python3
"""Use the bundled asset protocol, never create an independent schema."""
import argparse,importlib.util,json,re,shutil,sys,tempfile
from pathlib import Path
REFERENCE=Path(__file__).resolve().parents[2]/'video-reference-kit/scripts/video_ref.py'
spec=importlib.util.spec_from_file_location('reference_backend',REFERENCE);ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
ref.PRODUCER='video-asset-library'
KINDS=['reference_video','image','audio','music_track','sound_effect','font','motion_capability','method','analysis_document','user_archived_video']
ROLES={'reference':'unverified','product-original':'product_ui_original','feedback':'feedback_context','context':'conversation_context','unverified':'unverified','final':'production_context'}
def copied(root,source):
 sha=ref.digest(source);ext=source.suffix.lower();ext=ext if re.fullmatch(r'\.[a-z0-9]{1,10}',ext) else '.bin'
 dest=root/'objects'/sha/('source'+ext)
 if not dest.resolve().is_relative_to(root):raise ValueError('素材目录越出库根目录')
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():
  if ref.digest(dest)!=sha:raise ValueError('库内副本哈希不符，先修复，不覆盖')
 else:
  with tempfile.NamedTemporaryFile(dir=dest.parent,delete=False) as f:temp=Path(f.name)
  try:
   shutil.copyfile(source,temp)
   if ref.digest(temp)!=sha or ref.digest(source)!=sha:raise ValueError('复制期间原件变化')
   temp.replace(dest)
  finally:temp.unlink(missing_ok=True)
 return dest

def main():
 p=argparse.ArgumentParser(description='建立自己的空素材库并持续积累；复用video-reference-kit同一SQLite协议')
 p.add_argument('--library');sub=p.add_subparsers(dest='command',required=True)
 sub.add_parser('init');sub.add_parser('stats')
 q=sub.add_parser('lookup');q.add_argument('--file',required=True)
 q=sub.add_parser('search');q.add_argument('query',nargs='?',default='');q.add_argument('--kind',choices=KINDS);q.add_argument('--scope',choices=['all','product-ui'],default='all');q.add_argument('--include-context',action='store_true')
 q=sub.add_parser('get');q.add_argument('id');q.add_argument('--scope',choices=['all','product-ui'],default='all')
 q=sub.add_parser('backup');q.add_argument('--out',required=True)
 q=sub.add_parser('ingest');q.add_argument('--file',required=True);q.add_argument('--title',required=True);q.add_argument('--kind',choices=KINDS,required=True);q.add_argument('--category',required=True);q.add_argument('--role',choices=ROLES,default='reference');q.add_argument('--url');q.add_argument('--rights',choices=['unknown','owned','licensed','generated'],default='unknown');q.add_argument('--rights-basis',default='');q.add_argument('--tags',nargs='*',default=[]);q.add_argument('--use',default='');q.add_argument('--analysis');q.add_argument('--product-name');q.add_argument('--provenance');q.add_argument('--inspection');q.add_argument('--archive-instruction')
 a=p.parse_args()
 if a.command=='init':
  if not a.library:raise ValueError('init须提供--library；已有统一库不要初始化')
  return ref.init_library(a)
 lib=ref.Library(a.library)
 if a.command=='stats':return lib.call('stats')
 if a.command=='lookup':return lib.call('lookup','--file',str(Path(a.file).expanduser().resolve()))
 if a.command=='search':
  opts=['search',a.query,'--scope',a.scope]
  if a.kind:opts+=['--kind',a.kind]
  if a.include_context:opts+=['--include-context']
  return lib.call(*opts)
 if a.command=='backup':
  if lib.shared:raise ValueError('统一库请使用既有备份入口，避免绕过其备份策略')
  return {**lib.call('backup',str(Path(a.out).expanduser().resolve())),'scope':'database_only','mediaBackedUp':False,'next':'同时备份objects和references目录；仅复制SQLite不含媒体'}
 if a.command=='get':
  item=lib.call('get',a.id,'--scope',a.scope);verified=[]
  for obj in item.get('objects',[]):
   candidates=list((lib.root/'objects'/obj['sha']).glob('source.*')) if lib.root else []
   candidates += [Path(v['path']) for v in obj.get('locations',[])]
   for path in dict.fromkeys(candidates):
    if path.is_file() and ref.digest(path)==obj['sha']:verified.append({'path':str(path),'sha256':obj['sha']});break
  item['catalogNotes']=None
  if any(h.get('producer')==ref.PRODUCER and h.get('stream')=='catalog-notes' for h in item.get('resultHeads',[])):
   latest=lib.call('read-result',a.id,'--producer',ref.PRODUCER,'--stream','catalog-notes')
   item['catalogNotes']=json.loads(latest['payload']['documents'][0]['body'])
  item['verifiedLocalFiles']=verified;item['permissionMeaning']='登记和检索不代表已获素材使用权、真实功能认可或用户批准';return item
 if lib.read_only:raise ValueError('统一库当前是只读配置')
 source=Path(a.file).expanduser().resolve()
 if not source.is_file():raise ValueError('原件不存在')
 if not a.title.strip() or not a.category.strip():raise ValueError('标题和用途分类不能为空')
 if a.rights!='unknown' and not a.rights_basis.strip():raise ValueError('声明自有、生成或已授权时须记录实际依据')
 if a.role=='product-original':
  if a.kind not in ['reference_video','image'] or not all([a.product_name,a.provenance,a.inspection]):raise ValueError('产品原片须是图片/视频，并提供产品名、出处和实际检查范围')
 if a.role=='final' or a.kind=='user_archived_video':
  if a.role!='final' or a.kind!='user_archived_video' or not (a.archive_instruction or '').strip():raise ValueError('成片入库须使用final角色、user_archived_video类型并记录用户明确归档指令；候选只留项目')
 analysis=Path(a.analysis).expanduser().resolve().read_text(encoding='utf-8') if a.analysis else None
 prior=lib.call('lookup','--file',str(source))
 if prior.get('match')=='excluded':raise ValueError('原件已排除，不能重新启用')
 for item in prior.get('records',[]):
  if item['kind']==a.kind:
   old=lib.call('get',item['id'])
   if old.get('metadata',{}).get('evidenceRole','unverified')!=ROLES[a.role]:raise ValueError('同内容已有不同证据角色，先复核原记录，拒绝静默升级')
 local=source if lib.shared else copied(lib.root,source)
 opts=['register','--file',str(local),'--title',a.title,'--kind',a.kind,'--category',a.category,'--evidence-role',ROLES[a.role]]
 if a.url:opts+=['--url',a.url]
 if a.role=='product-original':opts+=['--product-name',a.product_name,'--source-provenance',a.provenance,'--inspection-scope',a.inspection]
 item=lib.call(*opts)
 body={'sourceSha256':ref.digest(local),'role':a.role,'tags':a.tags,'use':a.use,'rights':{'status':a.rights,'basis':a.rights_basis,'meaning':'recorded_declaration_not_license_verification'},'archiveInstruction':a.archive_instruction,'analysis':analysis,'analysisReview':'not_promoted_by_registration'}
 result=ref.submit(lib,item['id'],'catalog-notes',[{'key':'catalog-notes','body':json.dumps(body,ensure_ascii=False,sort_keys=True),'format':'.json'}])
 return {'state':'registered','assetId':item['id'],'localFile':str(local),'sourceSha256':body['sourceSha256'],'notes':result,'userApproved':False,'libraryMode':'existing_shared' if lib.shared else 'own_portable','cloudBackup':'not_performed','transactionScope':'file registration and notes are two steps; retry same command if notes fail; no overall atomicity claim'}
if __name__=='__main__':
 try:print(json.dumps(main(),ensure_ascii=False,indent=2))
 except (ValueError,OSError,KeyError,ref.subprocess.SubprocessError) as e:print(json.dumps({'state':'failed','error':str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(1)
