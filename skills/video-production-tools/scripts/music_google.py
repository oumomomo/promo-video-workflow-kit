#!/usr/bin/env python3
"""Google Lyria music: API-key or explicitly chosen Vertex ADC, verified cache, no automatic paid retry."""
import argparse,base64,datetime,getpass,hashlib,json,os,re,ssl,subprocess,sys,urllib.request,urllib.error
from pathlib import Path
SERVICE='video-workflow-gemini-api-key'
PRICE_URL='https://ai.google.dev/gemini-api/docs/pricing'
DOC_URL='https://ai.google.dev/gemini-api/docs/generate-content/music-generation'
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');temp.replace(path)
def context():
 try:
  import certifi
  return ssl.create_default_context(cafile=certifi.where())
 except ImportError:return ssl.create_default_context()
def api_key():
 key=os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
 if key:return key
 if sys.platform=='darwin':
  p=subprocess.run(['security','find-generic-password','-s',SERVICE,'-w'],capture_output=True,text=True)
  if p.returncode==0 and p.stdout.strip():return p.stdout.strip()
 raise ValueError('未配置自己的GEMINI_API_KEY；可用configure-key交互填写，或设置环境变量')
def adc_token():
 p=subprocess.run(['gcloud','auth','application-default','print-access-token'],capture_output=True,text=True)
 if p.returncode or not p.stdout.strip():raise ValueError('使用者Google ADC尚未配置；未发起生成')
 return p.stdout.strip()
def configure():
 if sys.platform!='darwin':raise ValueError('此系统请在自己的受保护环境中设置GEMINI_API_KEY，不把密钥写入项目')
 key=getpass.getpass('填写你自己的Google AI Studio API Key（不回显）: ').strip()
 if not key:raise ValueError('Key为空')
 p=subprocess.run(['security','add-generic-password','-U','-a',SERVICE,'-s',SERVICE,'-w',key],capture_output=True,text=True)
 if p.returncode:raise ValueError('钥匙串保存失败；未在项目写入密钥')
 return {'state':'key_saved_in_current_user_keychain','service':SERVICE,'keyDisplayed':False}
def make_request(prompt,auth,model,project):
 if not re.fullmatch(r'[a-zA-Z0-9._-]+',model):raise ValueError('模型ID无效')
 if auth=='api-key':return f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',{'contents':[{'parts':[{'text':prompt}]}]}
 if not project or not re.fullmatch(r'[a-zA-Z0-9._:-]+',project):raise ValueError('ADC模式须显式指定自己的--project-id或GOOGLE_CLOUD_PROJECT')
 return f'https://aiplatform.googleapis.com/v1beta1/projects/{project}/locations/global/interactions',{'model':model,'input':[{'type':'text','text':prompt}]}
def audio_parts(response):
 parts=[]
 for c in response.get('candidates',[]):
  if c.get('finishReason') not in (None,'STOP'):raise ValueError('模型返回未完整结束；不自动重试')
  for p in c.get('content',{}).get('parts',[]):
   data=p.get('inlineData') or p.get('inline_data')
   if data:parts.append((data.get('mimeType') or data.get('mime_type'),data.get('data')))
 for p in response.get('outputs',[]):
  if p.get('type')=='audio':parts.append((p.get('mime_type'),p.get('data')))
 for step in response.get('steps',[]):
  if step.get('type')=='model_output':
   for p in step.get('content',[]):
    if p.get('type')=='audio':parts.append((p.get('mime_type') or p.get('mimeType'),p.get('data')))
 return parts
def probe(path):
 p=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],capture_output=True,text=True)
 if p.returncode:raise ValueError('生成音频无法解码')
 data=json.loads(p.stdout);duration=float(data['format']['duration'])
 if not any(x['codec_type']=='audio' for x in data['streams']) or duration<=0:raise ValueError('无有效音频')
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','null','-'],check=True,capture_output=True)
 return {'durationSeconds':duration,'bytes':Path(path).stat().st_size,'sha256':digest(path),'fullDecode':'pass','listening':'pending'}
def generate(args):
 prompt=Path(args.prompt_file).read_text().strip()
 if not prompt:raise ValueError('音乐方向为空')
 endpoint,body=make_request(prompt,args.auth,args.model,args.project_id)
 request_hash=hashlib.sha256(json.dumps({'endpoint':endpoint,'body':body},sort_keys=True).encode()).hexdigest()
 unit={'lyria-3-clip-preview':.04,'lyria-3-pro-preview':.08,'lyria-3.5':.08}.get(args.model)
 metadata={'provider':'Google Gemini API' if args.auth=='api-key' else 'Google Vertex AI','authMode':args.auth,'model':args.model,'requestSha256':request_hash,'endpoint':endpoint,'pricingChecked':'2026-10-29','pricingSource':PRICE_URL if args.auth=='api-key' else 'https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing','estimatedUsdPerRequest':unit,'estimateMeaning':'published per-song estimate; actual account bill may differ','input':'text prompt only; no source media or credentials stored'}
 if args.dry_run:return {**metadata,'state':'dry_run','newRequests':0,'estimatedNewUsd':0,'wouldSendOneRequest':True}
 out=Path(args.output_dir).resolve();manifest=out/'generation.json'
 if manifest.exists():
  previous=json.loads(manifest.read_text())
  if previous.get('requestSha256')!=request_hash:raise ValueError('目录已绑定另一请求；保留旧记录，另建候选目录')
  if previous.get('state')=='completed':
   file=out/previous['audio']['file']
   if not file.is_file() or digest(file)!=previous['audio']['sha256']:raise ValueError('音乐缓存缺失或变更；不自动重新计费生成')
   probe(file);receipt={**previous,'state':'cache_hit','newRequests':0,'estimatedNewUsd':0};save(out/'last-use.json',receipt);return receipt
  if previous.get('newRequests',0):raise ValueError('已有发出、失败或不确定的请求记录；检查原记录，不自动重复生成')
 out.mkdir(parents=True,exist_ok=True);lock=out/'.generation.lock'
 try:lock.mkdir()
 except FileExistsError:raise ValueError('同目录已有生成任务或遗留锁，先检查，不重复发起')
 record={**metadata,'state':'preparing','newRequests':0,'estimatedNewUsd':0}
 try:
  secret=api_key() if args.auth=='api-key' else adc_token()
  headers={'Content-Type':'application/json'}
  if args.auth=='api-key':headers['x-goog-api-key']=secret
  else:headers.update(Authorization='Bearer '+secret,**{'x-goog-user-project':args.project_id})
  save(out/'request.json',body)
  record.update(state='request_sent',newRequests=1,estimatedNewUsd=unit);save(manifest,record)
  request=urllib.request.Request(endpoint,data=json.dumps(body).encode(),headers=headers,method='POST')
  try:
   with urllib.request.urlopen(request,context=context(),timeout=300) as response:result=json.load(response)
  except urllib.error.HTTPError as error:
   record.update(state='failed',httpStatus=error.code,error='provider_http_error_response_not_logged');save(manifest,record);raise ValueError('Google音乐请求失败；状态码见generation.json，不自动重试') from None
  except Exception as error:
   record.update(state='uncertain',error=type(error).__name__);save(manifest,record);raise ValueError('请求结果不确定；保留记录，禁止自动重发') from None
  save(out/'response-summary.json',{'id':result.get('id'),'status':result.get('status'),'usageMetadata':result.get('usageMetadata'),'audioCount':len(audio_parts(result))})
  parts=audio_parts(result)
  if len(parts)!=1:raise ValueError('未返回唯一完整音频，保留请求记录，不重试')
  mime,encoded=parts[0]
  if mime not in ['audio/mpeg','audio/mp3','audio/wav','audio/x-wav','audio/wave']:raise ValueError('未知音频类型')
  file=out/('bgm-generated.wav' if 'wav' in mime else 'bgm-generated.mp3');file.write_bytes(base64.b64decode(encoded,validate=True));info=probe(file)
  record.update(state='completed',audio={'file':file.name,**info},completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),operationId=result.get('id'))
  save(manifest,record)
  (out/'generation-evidence.txt').write_text('本次新生成的Google Lyria音乐。\n'+json.dumps(record,ensure_ascii=False,indent=2)+'\n生成身份不等于独占版权或发布批准；使用者须遵守自己的Google服务协议。服务条款：https://ai.google.dev/gemini-api/terms\n')
  return record
 except Exception:
  if record['newRequests']==0:record.update(state='auth_failed');save(manifest,record)
  elif record['state']=='request_sent':record.update(state='uncertain');save(manifest,record)
  raise
 finally:lock.rmdir()
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True);sub.add_parser('configure-key')
 a=sub.add_parser('generate');a.add_argument('--prompt-file',required=True);a.add_argument('--output-dir',required=True);a.add_argument('--auth',choices=['api-key','adc'],default='api-key');a.add_argument('--model',default='lyria-3-clip-preview');a.add_argument('--project-id',default=os.environ.get('GOOGLE_CLOUD_PROJECT',''));a.add_argument('--dry-run',action='store_true')
 args=p.parse_args();return configure() if args.command=='configure-key' else generate(args)
if __name__=='__main__':
 try:print(json.dumps(main(),ensure_ascii=False,indent=2))
 except Exception as error:print(json.dumps({'state':'failed','error':str(error)},ensure_ascii=False),file=sys.stderr);raise SystemExit(1)
