#!/usr/bin/env python3
"""Resumable reference analysis. Artifacts are caches; shared gateway is the sole library."""
import argparse,base64,hashlib,html,importlib.util,json,os,re,subprocess,sys,time
from pathlib import Path
VERSION='auto-reference-v1'
_TOKEN=None
_TOKEN_TIME=0
PROJECT=os.environ.get('GOOGLE_CLOUD_PROJECT','')
MODEL=os.environ.get('VIDEO_ANALYSIS_MODEL','gemini-2.5-flash')
ENDPOINT=f'https://aiplatform.googleapis.com/v1beta1/projects/{PROJECT}/locations/us-central1/publishers/google/models/{MODEL}:generateContent'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
VERSION='portable-reference-v1:'+hashlib.sha256(ENDPOINT.encode()).hexdigest()[:12]
def read(p):return json.loads(Path(p).read_text())
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2));os.replace(tmp,p)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def run(cmd):return subprocess.run([str(v) for v in cmd],check=True,capture_output=True,text=True)
from runtime import gateway

def analysis_windows(duration):
 if duration<=0:raise ValueError('duration must be positive')
 ranges=[(float(start),min(duration,start+10.0)) for start in range(0,int(duration)+1,10) if start<duration]
 if len(ranges)>1 and ranges[-1][1]-ranges[-1][0]<.25:
  ranges[-2]=(ranges[-2][0],ranges[-1][1]);ranges.pop()
 return ranges

def reusable_window(state,start,end):
 return state.get('version')==VERSION and abs(state.get('start',-1)-start)<1e-6 and abs(state.get('end',-1)-end)<1e-6

def normalize(review,duration):
 """Mechanical validation never promotes semantic confidence."""
 warnings=[]
 for key in ['visual','sfx','unclassified','sync']:
  if not isinstance(review.get(key),list):review[key]=[]
 for key in ['visual','sfx','unclassified']:
  valid=[]
  for e in review.get(key,[]):
   if not isinstance(e,dict):warnings.append(key+': invalid entry');continue
   try:a,b=float(e['start']),float(e['end'])
   except (KeyError,TypeError,ValueError):warnings.append(key+': invalid timestamps');continue
   if b>duration and b<=duration+.05:b=duration
   if not 0<=a<b<=duration:warnings.append(key+': out of range');continue
   e=dict(e,start=a,end=b,status='model_candidate')
   if key=='sfx' and (b-a>3 or str(e.get('category','')).lower() in ['music_percussion','speech','bgm','music','voiceover','口播','配乐','背景音乐','音乐鼓点','鼓点']):
    warnings.append('sfx: music/speech/long event moved to unclassified');e['reason']='not reliably isolated SFX';review.setdefault('unclassified',[]).append(e);continue
   valid.append(e)
  review[key]=valid
 # Repetitive generated grids are not evidence of independent sound effects.
 groups={}
 for e in review['sfx']:groups.setdefault(e.get('description',''),[]).append(e)
 suspect=[]
 for group in groups.values():
  ordered=sorted(group,key=lambda e:e['start'])
  gaps=[b['start']-a['start'] for a,b in zip(ordered,ordered[1:])]
  if len(group)>=4 and gaps and max(gaps)-min(gaps)<.03:suspect.extend(group)
 if suspect:
  warnings.append('repetitive SFX timing grid quarantined; sync is untrusted')
  for e in suspect:
   review['sfx'].remove(e);review['unclassified'].append(dict(e,reason='重复等间距音效时间表，不能确认为独立音效'))
 valid_sync=[]
 for e in review['sync']:
  if not isinstance(e,dict) or not all(isinstance(e.get(k),(int,float)) and 0<=e[k]<=duration for k in ['visualTime','audioTime']):warnings.append('invalid sync timestamps');continue
  valid_sync.append(dict(e,status='model_candidate_not_verified_sync',**({'qualityWarning':'音效时间表可疑，卡点未验证'} if suspect else {})))
 review['sync']=valid_sync
 if len(review.get('sfx',[]))>12:
  warnings.append('excessive SFX count quarantined; timing untrusted')
  review['unclassified'].extend(dict(e,reason='模型音效清单异常膨胀，待辨认') for e in review['sfx']);review['sfx']=[]
 return review,warnings

def enforce_no_audio(review,warnings):
 """Discard sound claims when ffprobe confirms the source has no audio stream."""
 if any(review.get(key) for key in ('bgm','sfx','unclassified','sync')) or (review.get('voiceover') or {}).get('present'):
  warnings.append('source has no audio stream; model sound claims discarded')
 review['bgm']=None
 review['voiceover']={'present':False}
 review['sfx']=[]
 review['unclassified']=[]
 review['sync']=[]
 return review,warnings

def infer(clip,mode,duration,attempt):
 import urllib.request
 if not PROJECT:raise ValueError('设置自己的GOOGLE_CLOUD_PROJECT后才可调用云端')
 global _TOKEN,_TOKEN_TIME
 spec=importlib.util.spec_from_file_location('auth',str(Path(__file__).resolve().parents[1]/'voice/scripts/voiceover_cli.py'));auth=importlib.util.module_from_spec(spec);spec.loader.exec_module(auth)
 if _TOKEN is None or time.monotonic()-_TOKEN_TIME>2400:
  try:_TOKEN=auth.access_token();_TOKEN_TIME=time.monotonic()
  except subprocess.CalledProcessError:raise RuntimeError('google_auth_refresh_failed') from None
 prompt='''使用简体中文。所有区间必须满足0<=start<end<=片段时长；不要用start=end代表瞬间，不确定时间则保留空数组。分析所附参考片段，严格返回JSON对象，所有时间为片段内秒数。必须分开：bgm对象（description, instruments, rhythm, entrance, ending）；voiceover对象（present, timbre, pace, pauses, emphasis）；sfx数组（start,end,description,category,functionCandidate）；unclassified数组（start,end,description,reason）；visual数组（start,end,composition,action,transition,evidenceDescription）；sync数组（visualTime,audioTime,description,uncertainty）。只描述可见可听证据。不知道填写null或空数组。BGM中的鼓点和旋律不可列为独立音效，口播不归音效。独立音效最多12个，禁止编造均匀时间表。音画关系无证据就留空。模型结果全部为候选。'''
 if mode=='audio':prompt+='本次仅有音轨，visual和sync必须为空，禁止猜画面。'
 prompt+='每个文字字段不超过80字。visual至多12项；sfx至多6项，不要求填满。禁止用固定间隔重复同一描述凑数；大量重复声只在unclassified用一个区间概述，不展开成音效表。'
 prompt+=f'片段时长为{duration:.3f}秒。画面请按持续动作区间描述，例如start:0,end:2.5，不要将全部事件起止写成相同时间。'
 body={'contents':[{'role':'user','parts':[{'text':prompt},{'inlineData':{'mimeType':'video/mp4' if mode=='video' else 'audio/mpeg','data':base64.b64encode(clip.read_bytes()).decode()}}]}],'generationConfig':{'temperature':0.2,'maxOutputTokens':6500,'thinkingConfig':{'thinkingBudget':0},'responseMimeType':'application/json'}}
 req=urllib.request.Request(ENDPOINT,data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+_TOKEN,'x-goog-user-project':PROJECT,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,context=auth.ssl_context(),timeout=180) as r:raw=json.load(r)
 except urllib.error.HTTPError as e:
  try:detail=json.loads(e.read()).get('error',{}).get('message','')
  except ValueError:detail=''
  save(attempt,{'httpStatus':e.code,'message':detail})
  raise RuntimeError(f'Google HTTP {e.code}: '+detail[:600]) from None
 texts=[p['text'] for c in raw.get('candidates',[]) for p in c.get('content',{}).get('parts',[]) if p.get('text') and not p.get('thought')]
 save(attempt,raw)
 if any(c.get('finishReason')!='STOP' for c in raw.get('candidates',[])):raise ValueError('incomplete_model_response')
 result=json.loads(''.join(texts))
 if not isinstance(result,dict):raise ValueError('expected object')
 result,warnings=normalize(result,duration)
 if mode=='video' and not result.get('visual'):raise ValueError('no_valid_visual_intervals')
 valid_sync=[]
 for e in result.get('sync',[]):
  if not isinstance(e,dict):continue
  e['status']='model_candidate_not_verified_sync'
  if not all(isinstance(e.get(k),(int,float)) and 0<=e[k]<=duration for k in ['visualTime','audioTime']):warnings.append('invalid sync timestamps');continue
  valid_sync.append(e)
 result['sync']=valid_sync
 if mode=='audio':result['visual']=[];result['sync']=[]
 return result,warnings

def process(source,out,cloud,authorized,submit,source_uri=None):
 source=source.resolve();digest=sha(source);out=out/digest[:16];out.mkdir(parents=True,exist_ok=True)
 if (out/'analysis.json').exists():
  previous=read(out/'analysis.json');canonical=Path(previous['source'])
  if canonical.is_file() and sha(canonical)==digest:source=canonical
  source_uri=source_uri or previous.get('sourceUri')
 save(out/'run-status.json',{'executionStatus':'running','stage':'analysis_and_evidence'})
 lookup=gateway('lookup','--file',str(source))
 if lookup.get('match')=='excluded':raise RuntimeError('source_excluded')
 probe_path=out/'probe.json'
 if not probe_path.exists():save(probe_path,json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',source]).stdout))
 probe=read(probe_path);duration=float(probe['format']['duration']);has_audio=any(s['codec_type']=='audio' for s in probe['streams'])
 # No 0.3-second suppression: short cuts remain candidates.
 cuts_path=out/'cuts.json'
 if not cuts_path.exists():
  r=run(['ffmpeg','-hide_banner','-i',source,'-vf',"select='gt(scene,0.08)',showinfo",'-an','-f','null','-']);cuts=[float(x) for x in re.findall(r'pts_time:([0-9.]+)',r.stderr)];save(cuts_path,{'status':'machine_candidate','threshold':.08,'times':cuts})
 windows=[]
 for start,end in analysis_windows(duration):
  name=f'{int(start):04d}';folder=out/'windows';folder.mkdir(exist_ok=True);state=folder/f'{name}-{cloud}-{VERSION.rsplit(chr(58),1)[-1]}.json'
  w={'start':start,'end':end,'status':'needs_cloud_authorization' if cloud=='none' else 'pending','sourceSha256':digest,'mode':cloud,'version':VERSION}
  if state.exists() and reusable_window(read(state),start,end):
   w=read(state)
   if w.get('status')=='candidate':
    w['analysis'],new_warnings=normalize(w.get('analysis',{}),end-start)
    w['warnings']=list(dict.fromkeys(w.get('warnings',[])+new_warnings))
    if not has_audio and cloud=='video':w['analysis'],w['warnings']=enforce_no_audio(w['analysis'],w['warnings'])
    if cloud=='video' and not w['analysis'].get('visual'):w['status']='invalid_visual_retry'
  if cloud!='none' and digest not in authorized:w['status']='needs_cloud_authorization'
  elif cloud!='none' and w.get('status')!='candidate':
   if cloud=='audio' and not has_audio:w['status']='no_audio'
   else:
    clip=folder/f'{name}-{end:.6f}.{ "mp4" if cloud=="video" else "mp3"}'
    if not clip.exists():
     cmd=['ffmpeg','-v','error','-y','-ss',start,'-i',source,'-t',end-start]
     cmd+=['-vf','scale=960:-2','-c:v','libx264','-crf','24','-preset','fast','-c:a','aac','-b:a','96k'] if cloud=='video' else ['-vn','-ac','1','-ar','24000','-b:a','96k']
     run(cmd+[clip])
    for attempt in range(3):
     w.update(status='running',attempt=attempt+1);save(state,w)
     try:
      began=time.monotonic();result,warnings=infer(clip,cloud,end-start,folder/f'{name}-{cloud}-attempt-{time.time_ns()}-{attempt+1}.json')
      if not has_audio and cloud=='video':result,warnings=enforce_no_audio(result,warnings)
      w.update(status='candidate',analysis=result,warnings=warnings,elapsedSeconds=round(time.monotonic()-began,2));w.pop('error',None);break
     except Exception as e:
      w.update(status='failed',error=type(e).__name__+': '+str(e)[:160])
      if attempt<2:time.sleep(2**attempt)
  save(state,w);windows.append(w)
  print(digest[:16],start,w['status'],flush=True)
 result={'version':VERSION,'sourceUri':source_uri,'source':str(source),'sourceSha256':digest,'duration':duration,'executionStatus':'completed_with_uncertainty' if all(w['status'] in ['candidate','no_audio'] for w in windows) else 'incomplete','semanticStatus':'model_candidates_not_human_approved','cuts':read(cuts_path),'windows':windows,'limitations':['Cut timestamps are machine candidates, not certified edit boundaries.','BGM, voiceover and SFX are separate; ambiguous audio is unclassified.','No stem separation or licensed reusable audio is implied.']}
 save(out/'analysis.json',result)
 md='# 自动拉片结果\n\n状态：'+result['executionStatus']+'。执行完成不等于语义全部确认。\n\n'
 blocks=[]
 for w in windows:
  md+=f'## {w["start"]}–{w["end"]} 秒\n\n状态：{w["status"]}\n\n'
  for key,label in [('visual','画面与动效'),('bgm','BGM'),('sfx','音效'),('voiceover','口播'),('unclassified','待辨认'),('sync','音画关系候选')]:
   text=json.dumps(w.get('analysis',{}).get(key),ensure_ascii=False,indent=2);md+=f'### {label}\n\n{text}\n\n';blocks.append('<details><summary>'+html.escape(f'{w["start"]}–{w["end"]}s · {label}')+'</summary><pre>'+html.escape(text)+'</pre></details>')
 (out/'REPORT.md').write_text(md);(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>自动拉片结果</title><style>body{max-width:1000px;margin:30px auto;padding:20px;font:16px/1.7 sans-serif}pre{white-space:pre-wrap}details{padding:12px;border-bottom:1px solid #ddd}</style><h1>自动拉片结果</h1><p>'+html.escape(result['executionStatus'])+' · 模型候选，未自动升级为人工确认</p>'+''.join(blocks))
 from precision import build as measure_precision
 from sound_reuse import build as prepare_reuse,eligible_assets
 from render_evidence import render as render_evidence
 precision=measure_precision(source,out,result)
 reuse=prepare_reuse(source,out,result,eligible_assets())
 render_evidence(out,precision,reuse)
 result['jev']={'status':'not_bundled','reason':'optional browser description service is outside this portable analyzer'}
 result['evidence']={'precision':'precision.json','soundReuse':'sound-reuse.json','handoff':'HANDOFF.md','frameChangeCandidates':len(precision['cuts']),'sfxCandidates':len(reuse['cards']),'sfxWithAlternatives':sum(bool(c['alternatives']) for c in reuse['cards']),'semanticStatus':'candidates_not_verified'}
 save(out/'analysis.json',result)
 with (out/'REPORT.md').open('a') as f:f.write('\n## 时间证据与音效复用\n\n[时间证据与对照试听](evidence.html) · [复用交接](HANDOFF.md)\n\n这些是自动证据与替代候选，不是已核准的切镜表、原作者音效或生产批准。\n')
 from render_report import render
 render(out,result)
 if submit:
  meta={'sourceSha256':digest,'assetId':source.stem,'analyzerVersion':VERSION,'sourceUri':''}
  # Adapter uses exact shared gateway contract with durable replay/version token.
  from runtime import submit_analysis as submit_result
  result['libraryReceipt']=submit_result(out,source,digest);save(out/'run-status.json',{'executionStatus':result['executionStatus'],'library':result['libraryReceipt']})
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',action='append',default=[]);p.add_argument('--url',action='append',default=[]);p.add_argument('--batch',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--cloud',choices=['none','audio','video'],default='none');p.add_argument('--authorization',type=Path);p.add_argument('--submit',action='store_true');p.add_argument('--browser-fallback',choices=['jev','none'],default='none');a=p.parse_args();sources=[Path(x) for x in a.source]
 url_sources={};intake_failures=[]
 for url in a.url:
  try:
   from intake import acquire
   path,receipt=acquire(url,a.out,a.browser_fallback);sources.append(path);url_sources[str(path.resolve())]=url
  except Exception as e:intake_failures.append({'url':url,'stage':'intake','error':type(e).__name__+': '+str(e)[:180]})
 if a.url or a.batch:p.error('便携分析器本轮只接受本地--source；先取得并校验原件，不调用私人浏览器执行器')
 if a.batch:sources += [a.batch/sid/'analysis-media-1/source.mp4' for user,sid in read(a.batch/'sources.json')]
 if not sources and not intake_failures:p.error('at least one source or batch is required')
 authorized=set()
 if a.authorization:
  grant=read(a.authorization)
  if grant.get('mode')!=a.cloud or grant.get('endpoint')!=ENDPOINT:p.error('authorization scope mismatch')
  authorized=set(grant['sourceHashes'])
 failures=intake_failures
 for source in sources:
  try:
   result=process(source,a.out,a.cloud,authorized,a.submit,url_sources.get(str(source.resolve())))
   if result['executionStatus']=='incomplete':failures.append({'source':str(source),'error':'incomplete_windows'})
  except Exception as e:
   error=type(e).__name__+': '+str(e)[:180];failures.append({'source':str(source),'error':error})
   if source.is_file():save(a.out/sha(source)[:16]/'run-status.json',{'executionStatus':'failed','error':error,'stage':'analysis_evidence_or_submit'})
 save(a.out/'batch-status.json',{'failures':failures,'sourceCount':len(sources)})
 if a.batch:run([sys.executable,Path(__file__).with_name('publish_dashboard.py'),'--batch',a.batch,'--out',a.out])
 if failures:sys.exit(1)
if __name__=='__main__':main()
