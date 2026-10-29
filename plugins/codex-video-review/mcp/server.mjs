import {createHash, randomUUID, randomBytes} from 'node:crypto';
import {createReadStream} from 'node:fs';
import {mkdir, readFile, readdir, realpath, rename, rm, stat, writeFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import {spawn} from 'node:child_process';
import {tmpdir} from 'node:os';
import {basename, dirname, extname, isAbsolute, join, relative, resolve, sep} from 'node:path';
import {existsSync, readFileSync} from 'node:fs';
import {McpServer} from '@modelcontextprotocol/sdk/server/mcp.js';
import {StdioServerTransport} from '@modelcontextprotocol/sdk/server/stdio.js';
import {registerAppResource, RESOURCE_MIME_TYPE} from '@modelcontextprotocol/ext-apps/server';
import {z} from 'zod';

const URI='ui://codex-video-review/review.html';
const SEND_MODEL='gpt-6-sol';
const DESKTOP_CODEX='/Applications/ChatGPT.app/Contents/Resources/codex';
const CODEX_BIN=process.env.CODEX_VIDEO_REVIEW_CODEX_BIN||process.env.CODEX_CLI_PATH||(existsSync(DESKTOP_CODEX)?DESKTOP_CODEX:'codex');
const sessions=new Map();
const media=createServer(async(req,res)=>{
  const pathname=new URL(req.url,'http://localhost').pathname;
  const route=/^\/(video|review|api\/save|api\/note|api\/send-capability|api\/send|api\/send-status)\/([a-f0-9]{48})$/.exec(pathname);
  const imageRoute=/^\/image\/([a-f0-9]{48})\/([a-f0-9]{64})$/.exec(pathname);
  const token=route?.[2]||imageRoute?.[1];
  const session=token&&sessions.get(token);
  if(!session){res.writeHead(404);res.end();return;}
  if(imageRoute){
    if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);res.end();return;}
    const notes=await readNotes(session.identity);
    const image=notes.notes.flatMap(note=>note.images||[]).find(item=>item.sha256===imageRoute[2]);
    if(!image||image.relativePath!==imageRelativePath(session.identity.sha256,image.sha256,image.mimeType)){res.writeHead(404);res.end();return;}
    try{
      const path=join(session.identity.root,image.relativePath),info=await stat(path);
      res.writeHead(200,{'Content-Type':image.mimeType,'Content-Length':info.size,'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'});
      if(req.method==='HEAD')res.end();else createReadStream(path).pipe(res);
    }catch{res.writeHead(404);res.end();}
    return;
  }
  if(route[1]==='review'){
    if(req.method!=='GET'){res.writeHead(405);res.end();return;}
    const latestNotes=await readNotes(session.identity);
    const bootstrap=`window.__VIDEO_REVIEW_BOOTSTRAP__=${JSON.stringify({...session.payload,notes:latestNotes.notes}).replaceAll('<','\\u003c')};`;
    const page=widget.replace('/*__BOOT__*/',()=>bootstrap);
    res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'private, no-store','Content-Security-Policy':"default-src 'self' blob: data:; script-src 'unsafe-inline'; style-src 'unsafe-inline'; media-src 'self' blob:; connect-src 'self';"});res.end(page);return;
  }
  if(route[1]==='api/save'){
    if(req.method!=='POST'){res.writeHead(405);res.end();return;}
    try{
      let body='';for await(const chunk of req){body+=chunk;if(body.length>40_000_000)throw new Error('标注或参考图过大');}
      const note=annotation.parse(JSON.parse(body));
      const current=await saveNote(session.identity,note);
      res.writeHead(200,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'});res.end(JSON.stringify(current));
    }catch(error){res.writeHead(400,{'Content-Type':'application/json; charset=utf-8'});res.end(JSON.stringify({error:error.message}));}return;
  }
  if(route[1]==='api/note'){
    if(req.method!=='POST'){res.writeHead(405);res.end();return;}
    if(req.headers.origin!==origin){res.writeHead(403);res.end();return;}
    try{
      let body='';for await(const chunk of req){body+=chunk;if(body.length>10000)throw new Error('标注请求过大');}
      const change=noteChange.parse(JSON.parse(body));
      const current=await changeNote(session.identity,change);
      res.writeHead(200,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'});res.end(JSON.stringify(current));
    }catch(error){res.writeHead(400,{'Content-Type':'application/json; charset=utf-8'});res.end(JSON.stringify({error:error.message}));}return;
  }
  if(route[1]==='api/send-capability'){
    if(req.method!=='GET'){res.writeHead(405);res.end();return;}
    let available=false,model=null;
    if(session.threadId){
      try{
        model=await withCodexThread(session.threadId,async(_request,sendModel)=>sendModel,null,true);
        available=await queueAvailable();
        if(!available){try{await withCodexThread(session.threadId,async()=>true);available=true;}catch{}}
      }catch{}
    }
    res.writeHead(200,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'});res.end(JSON.stringify({available,model}));return;
  }
  if(route[1]==='api/send-status'){
    if(req.method!=='GET'){res.writeHead(405);res.end();return;}
    const notes=await readNotes(session.identity);
    const summary=await sendSummary(session,notes.notes);
    res.writeHead(200,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'});
    res.end(JSON.stringify(summary));return;
  }
  if(route[1]==='api/send'){
    if(req.method!=='POST'){res.writeHead(405);res.end();return;}
    if(req.headers.origin!==origin){res.writeHead(403);res.end();return;}
    try{
      if(!session.threadId)throw new Error('此页面没有绑定 Codex 会话');
      const latest=await identify(session.identity.file,session.identity.root);
      if(latest.sha256!==session.identity.sha256)throw new Error('视频已变化，请重新打开打标页');
      const current=await readNotes(session.identity);
      if(!current.notes.length)throw new Error('请先保存标注');
      const summary=await sendSummary(session,current.notes);
      const pending=current.notes.filter(note=>summary.pendingNoteIds.includes(note.id));
      if(!pending.length){res.writeHead(200,{'Content-Type':'application/json; charset=utf-8'});res.end(JSON.stringify({...summary,duplicate:true}));return;}
      const fingerprint=notesFingerprint(pending);
      if(session.sendState?.fingerprint===fingerprint&&['submitting','queued','submitted','processing','completed'].includes(session.sendState.state)){
        res.writeHead(200,{'Content-Type':'application/json; charset=utf-8'});res.end(JSON.stringify({...session.sendState,duplicate:true}));return;
      }
      if(session.sendPending)throw new Error('请求正在发送，请稍候');
      session.sendPending=true;
      try{
        const receiptDir=sendReceiptDir(session.identity,session.threadId,fingerprint);
        await mkdir(dirname(receiptDir),{recursive:true});
        try{await mkdir(receiptDir);}catch(error){
          if(error.code!=='EEXIST')throw error;
          const existing=await readSendReceipt(receiptDir)||{state:'submitting',fingerprint,threadId:session.threadId};
          res.writeHead(200,{'Content-Type':'application/json; charset=utf-8'});res.end(JSON.stringify({...existing,duplicate:true}));return;
        }
        const prompt=buildReviewPrompt(session.identity,pending);
        const sendState={state:'submitting',fingerprint,threadId:session.threadId,turnId:null,assistantSeen:false,updatedAt:Date.now(),noteRevisions:pending.map(note=>({id:note.id,hash:notesFingerprint(note)}))};
        session.sendState=sendState;
        await writeSendReceipt(receiptDir,sendState);
        const changed=()=>{sendState.updatedAt=Date.now();writeSendReceipt(receiptDir,sendState).catch(()=>{});};
        const watch={
          onNotification(value){
            if(value.params?.threadId&&value.params.threadId!==session.threadId)return;
            if(sendState.turnId&&value.params?.turnId&&value.params.turnId!==sendState.turnId)return;
            if(sendState.turnId&&value.params?.turn?.id&&value.params.turn.id!==sendState.turnId)return;
            if(value.method==='item/started'||value.method==='item/completed'){
              const item=value.params?.item;
              if(item?.type==='agentMessage'||item?.type==='commandExecution'||item?.type==='mcpToolCall'){
                if(item.type==='agentMessage')sendState.assistantSeen=true;
                if(sendState.state==='submitted')sendState.state='processing';
                changed();
              }
            }
            if(value.method==='turn/completed'){
              const turn=value.params?.turn;
              if(!sendState.turnId||turn?.id!==sendState.turnId)return;
              sendState.state=turn?.status==='completed'&&sendState.assistantSeen?'completed':'failed';
              sendState.error=sendState.state==='failed'?(turn?.error?.message||'任务回合结束，但没有 AI 回复；修改未确认开始。'):null;
              changed();
              if(sendState.state==='failed')rm(receiptDir,{recursive:true,force:true}).catch(()=>{});
              return true;
            }
          },
          onExit(){if(['submitted','processing'].includes(sendState.state)){sendState.state='failed';sendState.error='Codex 会话连接中断，未确认 AI 完成处理';changed();rm(receiptDir,{recursive:true,force:true}).catch(()=>{});}}
        };
        void (async()=>{
          try{
            const started=await withCodexThread(session.threadId,async(request,sendModel)=>{sendState.model=sendModel;changed();return request('turn/start',{threadId:session.threadId,model:sendModel,input:[{type:'text',text:prompt}]});},watch);
            if(!started?.turn?.id)throw new Error('Codex 没有返回任务回合 ID');
            sendState.turnId=started.turn.id;
            sendState.state='submitted';
            changed();
          }catch(error){
            if(error.message.includes('already has an active writer')){
              try{
                await runCodexQueue(session.threadId,prompt);
                sendState.state='queued';sendState.delivery='codex-queue';sendState.model=SEND_MODEL;sendState.error=null;changed();return;
              }catch(queueError){error=queueError;}
            }
            sendState.state='failed';sendState.error=error.message;
            changed();await rm(receiptDir,{recursive:true,force:true}).catch(()=>{});
          }
        })().catch(error=>{sendState.state='failed';sendState.error=error.message;changed();rm(receiptDir,{recursive:true,force:true}).catch(()=>{});});
      }finally{session.sendPending=false;}
      res.writeHead(200,{'Content-Type':'application/json; charset=utf-8'});res.end(JSON.stringify({...session.sendState,duplicate:false}));
    }catch(error){if(session.sendState?.state==='submitting'){session.sendState.state='failed';session.sendState.error=error.message;await rm(sendReceiptDir(session.identity,session.threadId,session.sendState.fingerprint),{recursive:true,force:true}).catch(()=>{});}res.writeHead(503,{'Content-Type':'application/json; charset=utf-8'});res.end(JSON.stringify({error:error.message}));}return;
  }
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);res.end();return;}
  try{
    const info=await stat(session.path);
    const total=info.size;
    const range=/^bytes=(\d+)-(\d*)$/.exec(req.headers.range||'');
    const start=range?Number(range[1]):0;
    const end=range&&range[2]?Math.min(Number(range[2]),total-1):total-1;
    if(start>=total||end<start){res.writeHead(416,{'Content-Range':`bytes */${total}`});res.end();return;}
    res.writeHead(range?206:200,{
      'Content-Type':extname(session.path).toLowerCase()==='.webm'?'video/webm':'video/mp4',
      'Content-Length':end-start+1,'Accept-Ranges':'bytes',
      'Content-Range':`bytes ${start}-${end}/${total}`,
      'Cache-Control':'private, no-store','Access-Control-Allow-Origin':'*',
    });
    if(req.method==='HEAD'){res.end();return;}
    createReadStream(session.path,{start,end}).pipe(res);
  }catch{if(!res.headersSent)res.writeHead(500);res.end();}
});
await new Promise((ok,fail)=>media.once('error',fail).listen(0,'127.0.0.1',ok));
const origin=`http://127.0.0.1:${media.address().port}`;

function noteRegion(note){
  return note.marks.map(mark=>{
    const xs=mark.points.map(point=>point[0]),ys=mark.points.map(point=>point[1]);
    return `${mark.type} ${Math.round(Math.min(...xs)*100)}–${Math.round(Math.max(...xs)*100)}% 横向、${Math.round(Math.min(...ys)*100)}–${Math.round(Math.max(...ys)*100)}% 纵向`;
  }).join('；');
}
function buildReviewPrompt(identity,notes){
  const lines=notes.map((note,index)=>{
    const images=(note.images||[]).map(image=>join(identity.root,image.relativePath));
    return `${index+1}. 标注 ID ${note.id}，${note.time.toFixed(3)} 秒：${note.text}\n   此条对应的画面标记：${noteRegion(note)||'无'}${images.length?`\n   此条参考图：${images.join('；')}`:''}`;
  });
  return `请按以下 ${notes.length} 条视频标注修改当前候选片。同一时间点的标注是独立建议，每条文字仅对应它自己 ID 下的画面区域和参考图。参考图属于用户反馈，不自动视为产品 UI 原片。\n视频：${identity.file}\nSHA-256：${identity.sha256}\n${lines.join('\n')}\n精确画线坐标保存在 ${notesPath(identity.root,identity.sha256)}，需要定位时再读取。只修改标注涉及的片段，保留未标注镜头、总时长与音轨；交付时逐条核对。`;
}
function runProcess(command,args,{input='',timeoutMs=20000}={}){
  return new Promise((resolve,reject)=>{
    // The plugin cache may be replaced while this MCP process remains alive.
    // A child spawned from its removed working directory fails with ENOENT.
    const child=spawn(command,args,{cwd:tmpdir(),stdio:['pipe','pipe','pipe']});
    let output='';let settled=false;
    const finish=error=>{if(settled)return;settled=true;clearTimeout(timer);if(error)reject(error);else resolve(output);};
    const timer=setTimeout(()=>{child.kill();finish(new Error(`${command} 超时`));},timeoutMs);
    child.stdout.on('data',chunk=>{output=(output+chunk.toString()).slice(-3000);});
    child.stderr.on('data',chunk=>{output=(output+chunk.toString()).slice(-3000);});
    child.on('error',finish);
    child.on('exit',code=>finish(code===0?null:new Error(output.trim()||`${command} 退出码 ${code}`)));
    child.stdin.on('error',()=>{});
    child.stdin.end(input);
  });
}
async function runCodexQueue(threadId,message){
  const args=['queue','--thread',threadId,'--message',message,'-m',SEND_MODEL];
  return runProcess(CODEX_BIN,args,{timeoutMs:30000});
}
/* Queue preflight intentionally uses a nonexistent task, so it cannot create a real message. */
async function queueAvailable(){
  try{await runCodexQueue('00000000-0000-4000-8000-000000000000','codex-video-review capability probe');return false;}
  catch(error){return error.message.includes('no rollout found for thread id 00000000-0000-4000-8000-000000000000');}
}

async function withCodexThread(threadId,action,watch=null,readOnly=false){
  const child=spawn(CODEX_BIN,['app-server'],{cwd:tmpdir(),stdio:['pipe','pipe','pipe'],detached:Boolean(watch)});
  let buffer='',nextId=1,stderr='';const pending=new Map();
  let completed=false,turnStarted=false;
  child.stdout.on('data',chunk=>{buffer+=chunk.toString();for(let end;(end=buffer.indexOf('\n'))!==-1;){const line=buffer.slice(0,end);buffer=buffer.slice(end+1);try{const value=JSON.parse(line);if(value.id!=null){pending.get(value.id)?.(value);pending.delete(value.id);}else if(watch?.onNotification?.(value)===true){completed=true;child.kill();}}catch{}}});
  child.stderr.on('data',chunk=>{stderr=(stderr+chunk.toString()).slice(-1000);});
  child.on('error',error=>{for(const resolve of pending.values())resolve({error:{message:error.message}});pending.clear();});
  child.on('exit',()=>{if(turnStarted)watch?.onExit?.();for(const resolve of pending.values())resolve({error:{message:'Codex app-server 已退出'}});pending.clear();});
  const request=(method,params)=>new Promise((resolve,reject)=>{
    const id=nextId++;const timeout=method==='thread/resume'?60000:method==='turn/start'?30000:10000;
    const timer=setTimeout(()=>{pending.delete(id);reject(new Error(`Codex ${method} 超时`));},timeout);
    pending.set(id,value=>{clearTimeout(timer);if(value.error)reject(new Error(value.error.message));else resolve(value.result);});
    child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method,params})+'\n');
  });
  try{
    await request('initialize',{clientInfo:{name:'codex-video-review',version:'0.1.0'},capabilities:{experimentalApi:true}});
    child.stdin.write(JSON.stringify({jsonrpc:'2.0',method:'initialized'})+'\n');
    // turn/start requires a resumed task. Exclude its long rollout from the response.
    const result=await request(readOnly?'thread/read':'thread/resume',readOnly?{threadId,includeTurns:false}:{threadId,excludeTurns:true});
    if(result?.thread?.id!==threadId)throw new Error('Codex 会话身份不匹配');
    const models=await request('model/list',{});
    if(!models?.data?.some(model=>model.model===SEND_MODEL))throw new Error(`当前 Codex 执行器不支持 ${SEND_MODEL}，不会改用其他模型发送`);
    const actionResult=await action(request,SEND_MODEL);turnStarted=Boolean(watch);return actionResult;
  }catch(error){if(stderr.includes('readonly database'))throw new Error('Codex 未允许插件访问会话状态');throw error;}
  finally{if(!turnStarted)child.kill();else if(!completed){const timeout=setTimeout(()=>child.kill(),30*60*1000);timeout.unref();child.unref();}}
}

const app=new McpServer({name:'codex-video-review',version:'0.1.0'},{instructions:'Open local project videos in a native Codex review widget. Read saved annotations before modifying a video. Bind edits to the saved file SHA-256 and time/mark coordinates; preserve unmarked shots.'});
const html=readFileSync(new URL('../web/index.html',import.meta.url),'utf8');
const js=readFileSync(new URL('../dist/widget.js',import.meta.url),'utf8').replaceAll('</script','<\\/script');
const css=readFileSync(new URL('../web/style.css',import.meta.url),'utf8');
const widget=html.replace('/*__STYLE__*/',()=>css).replace('/*__SCRIPT__*/',()=>js);
const meta={ui:{prefersBorder:false,csp:{connectDomains:[origin],resourceDomains:[origin,'blob:','data:']}},'openai/widgetCSP':{connect_domains:[origin],resource_domains:[origin,'blob:','data:']}};
registerAppResource(app,'video-review-widget',URI,{title:'视频打标',_meta:meta},async()=>({contents:[{uri:URI,mimeType:RESOURCE_MIME_TYPE,text:widget,_meta:meta}]}));

async function identify(filePath,projectDir){
  if(!isAbsolute(filePath)||!isAbsolute(projectDir))throw new Error('请传入视频和项目目录的绝对路径');
  const root=await realpath(projectDir),file=await realpath(filePath);
  const rel=relative(root,file);
  if(!rel||rel==='..'||rel.startsWith(`..${sep}`)||isAbsolute(rel))throw new Error('视频必须位于指定项目目录内');
  if(!['.mp4','.mov','.m4v','.webm'].includes(extname(file).toLowerCase()))throw new Error('只支持本地视频文件');
  const info=await stat(file);if(!info.isFile())throw new Error('视频路径不是文件');
  const hash=createHash('sha256');for await(const chunk of createReadStream(file))hash.update(chunk);
  return {root,file,sha256:hash.digest('hex'),size:info.size,name:basename(file)};
}
const input={projectDir:z.string(),filePath:z.string()};
const imageMime=z.enum(['image/png','image/jpeg','image/webp','image/gif']);
const incomingImage=z.object({name:z.string().min(1).max(200),mimeType:imageMime,dataUrl:z.string().max(11_000_000)});
const annotation=z.object({
  id:z.string().min(8).max(100),time:z.number().finite().min(0),
  endTime:z.number().finite().min(0).optional(),text:z.string().trim().min(1).max(2000),
  marks:z.array(z.object({type:z.enum(['pen','line','arrow','box']),points:z.array(z.tuple([z.number().min(0).max(1),z.number().min(0).max(1)])).min(2).max(300)})).max(30),
  images:z.array(incomingImage).max(5).optional(),
});
const noteChange=z.discriminatedUnion('action',[
  z.object({action:z.literal('update'),id:z.string().min(8).max(100),text:z.string().trim().min(1).max(2000)}),
  z.object({action:z.literal('delete'),id:z.string().min(8).max(100)}),
]);
function notesPath(root,sha){return join(root,'.codex-video-review',`${sha}.json`);}
const imageExtensions={'image/png':'png','image/jpeg':'jpg','image/webp':'webp','image/gif':'gif'};
function imageRelativePath(videoSha,imageSha,mimeType){return join('.codex-video-review','attachments',videoSha,`${imageSha}.${imageExtensions[mimeType]}`);}
async function persistImages(video,images=[]){
  let total=0;
  return Promise.all(images.map(async image=>{
    const match=/^data:([^;,]+);base64,([A-Za-z0-9+/=]+)$/.exec(image.dataUrl);
    if(!match||match[1]!==image.mimeType)throw new Error('参考图格式不正确');
    const bytes=Buffer.from(match[2],'base64');total+=bytes.length;
    if(!bytes.length||bytes.length>8_000_000||total>24_000_000)throw new Error('参考图每张最多 8 MB，总计最多 24 MB');
    const sha256=createHash('sha256').update(bytes).digest('hex');
    const relativePath=imageRelativePath(video.sha256,sha256,image.mimeType);
    const path=join(video.root,relativePath);await mkdir(dirname(path),{recursive:true});
    try{await writeFile(path,bytes,{flag:'wx'});}catch(error){if(error.code!=='EEXIST')throw error;}
    return {name:image.name,mimeType:image.mimeType,size:bytes.length,sha256,relativePath};
  }));
}
function notesFingerprint(notes){return createHash('sha256').update(JSON.stringify(notes)).digest('hex');}
function sendReceiptDir(identity,threadId,fingerprint){return join(identity.root,'.codex-video-review','send',identity.sha256,threadId,fingerprint);}
const acceptedSendStates=new Set(['queued','submitted','processing','completed']);
async function sendSummary(session,notes){
  const base=join(session.identity.root,'.codex-video-review','send',session.identity.sha256);
  let threads=[];try{threads=await readdir(base,{withFileTypes:true});}catch(error){if(error.code!=='ENOENT')throw error;}
  const receiptDirs=(await Promise.all(threads.filter(entry=>entry.isDirectory()).map(async entry=>{
    const threadDir=join(base,entry.name);
    return (await readdir(threadDir,{withFileTypes:true})).filter(child=>child.isDirectory()).map(child=>join(threadDir,child.name));
  }))).flat();
  const receipts=(await Promise.all(receiptDirs.map(async dir=>({dir,receipt:await readSendReceipt(dir)})))).filter(item=>item.receipt);
  const fullFingerprint=notesFingerprint(notes);
  const revisions=new Set();
  for(const {dir,receipt} of receipts){
    if(!acceptedSendStates.has(receipt.state))continue;
    if(!receipt.noteRevisions&&receipt.fingerprint===fullFingerprint){
      receipt.noteRevisions=notes.map(note=>({id:note.id,hash:notesFingerprint(note)}));
      await writeSendReceipt(dir,receipt);
    }
    for(const revision of receipt.noteRevisions||[])revisions.add(`${revision.id}:${revision.hash}`);
  }
  const sentNoteIds=notes.filter(note=>revisions.has(`${note.id}:${notesFingerprint(note)}`)).map(note=>note.id);
  const sent=new Set(sentNoteIds),pendingNoteIds=notes.filter(note=>!sent.has(note.id)).map(note=>note.id);
  const latest=[...receipts.map(item=>item.receipt),session.sendState].filter(Boolean).sort((a,b)=>(b.updatedAt||0)-(a.updatedAt||0))[0];
  return {...(latest||{state:'not-sent'}),sentNoteIds,pendingNoteIds};
}
async function readSendReceipt(dir){
  try{return JSON.parse(await readFile(join(dir,'state.json'),'utf8'));}catch(error){if(error.code==='ENOENT')return null;throw error;}
}
async function writeSendReceipt(dir,state){
  const temp=join(dir,`${randomUUID()}.tmp`);
  await writeFile(temp,JSON.stringify(state)+'\n',{flag:'wx'});
  await rename(temp,join(dir,'state.json'));
}
async function readNotes(identity){
  try{const value=JSON.parse(await readFile(notesPath(identity.root,identity.sha256),'utf8'));
    if(value.sha256!==identity.sha256)throw new Error('标注文件的视频哈希不匹配');return value;
  }catch(e){if(e.code==='ENOENT')return {version:1,video:identity.file,sha256:identity.sha256,notes:[]};throw e;}
}
function output(value){return {content:[{type:'text',text:JSON.stringify(value)}],structuredContent:value};}
async function saveNote(video,note){
  const latest=await identify(video.file,video.root);if(latest.sha256!==video.sha256)throw new Error('视频已变化，请重新打开后再标注');
  const current=await readNotes(video);if(current.notes.some(n=>n.id===note.id))return current;
  note={...note,images:await persistImages(video,note.images)};
  current.notes.push(note);current.notes.sort((a,b)=>a.time-b.time);
  const path=notesPath(video.root,video.sha256);await mkdir(dirname(path),{recursive:true});
  const temp=`${path}.${randomUUID()}.tmp`;await writeFile(temp,JSON.stringify(current,null,2)+'\n',{flag:'wx'});await rename(temp,path);
  return current;
}
async function changeNote(video,change){
  const latest=await identify(video.file,video.root);if(latest.sha256!==video.sha256)throw new Error('视频已变化，请重新打开打标页');
  const current=await readNotes(video),index=current.notes.findIndex(note=>note.id===change.id);
  if(index<0)throw new Error('这条标注已不存在，请刷新页面');
  if(change.action==='delete')current.notes.splice(index,1);
  else current.notes[index].text=change.text;
  const path=notesPath(video.root,video.sha256),temp=`${path}.${randomUUID()}.tmp`;
  await writeFile(temp,JSON.stringify(current,null,2)+'\n',{flag:'wx'});await rename(temp,path);
  return current;
}

app.registerTool('open_video_review',{title:'打开视频打标',description:'创建本地视频打标页并返回 reviewUrl。调用后用 Codex 的 open_in_codex 将 reviewUrl 打开在右侧浏览器面板，不要在会话消息内嵌播放器。传入项目根目录和视频绝对路径。',inputSchema:input},
  async({projectDir,filePath},extra)=>{
    const video=await identify(filePath,projectDir);
    const token=randomBytes(24).toString('hex');
    const candidateThreadId=extra?._meta?.['openai/threadId']||extra?._meta?.['codexThreadId']||extra?._meta?.['threadId']||process.env.CODEX_THREAD_ID||null;
    const threadId=typeof candidateThreadId==='string'&&/^[a-f0-9-]{36}$/i.test(candidateThreadId)?candidateThreadId:null;
    const payload={video:{name:video.name,path:video.file,sha256:video.sha256,size:video.size,url:`${origin}/video/${token}`},projectDir:video.root,notes:(await readNotes(video)).notes,boundThreadId:threadId,preferredDisplayMode:'fullscreen',reviewUrl:`${origin}/review/${token}`,imageBaseUrl:`${origin}/image/${token}/`,saveUrl:`${origin}/api/save/${token}`,noteUrl:`${origin}/api/note/${token}`,sendUrl:`${origin}/api/send/${token}`,sendStatusUrl:`${origin}/api/send-status/${token}`,sendCapabilityUrl:`${origin}/api/send-capability/${token}`};
    sessions.set(token,{path:video.file,identity:video,payload,threadId});
    return output(payload);
  });
app.registerTool('get_video_review_notes',{title:'读取视频标注',description:'读取绑定到本地视频 SHA-256 的时间点、画面标记和修改文字。',inputSchema:input,annotations:{readOnlyHint:true}},
  async({projectDir,filePath})=>{const video=await identify(filePath,projectDir);return output(await readNotes(video));});
app.registerTool('save_video_review_note',{title:'保存视频标注',description:'从视频打标组件保存一条绑定视频哈希的意见；同一 id 重试不会重复。',inputSchema:{...input,sha256:z.string().regex(/^[a-f0-9]{64}$/),note:annotation}},
  async({projectDir,filePath,sha256,note})=>{
    const video=await identify(filePath,projectDir);if(video.sha256!==sha256)throw new Error('视频已变化，请重新打开后再标注');
    return output(await saveNote(video,note));
  });
app.registerTool('update_video_review_note',{title:'修改视频标注',description:'修改绑定视频哈希的一条标注文字。',inputSchema:{...input,sha256:z.string().regex(/^[a-f0-9]{64}$/),id:z.string().min(8).max(100),text:z.string().trim().min(1).max(2000)}},
  async({projectDir,filePath,sha256,id,text})=>{const video=await identify(filePath,projectDir);if(video.sha256!==sha256)throw new Error('视频已变化，请重新打开打标页');return output(await changeNote(video,{action:'update',id,text}));});
app.registerTool('delete_video_review_note',{title:'删除视频标注',description:'删除绑定视频哈希的一条标注。',inputSchema:{...input,sha256:z.string().regex(/^[a-f0-9]{64}$/),id:z.string().min(8).max(100)}},
  async({projectDir,filePath,sha256,id})=>{const video=await identify(filePath,projectDir);if(video.sha256!==sha256)throw new Error('视频已变化，请重新打开打标页');return output(await changeNote(video,{action:'delete',id}));});
await app.connect(new StdioServerTransport());
