import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
import {mkdtemp,writeFile,readFile,rm,mkdir,chmod} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {Script} from 'node:vm';
import {execFileSync} from 'node:child_process';

function checkScripts(html,expected){
  const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(match=>match[1]);
  if(scripts.length!==expected)throw Error(`broken HTML script boundaries: ${scripts.length}`);
  for(const script of scripts)new Script(script);
}

const dir=await mkdtemp(join(tmpdir(),'codex-video-review-test-'));
const file=join(dir,'sample.mp4');await writeFile(file,Buffer.from('fake-video-for-api-test'));
const client=new Client({name:'probe',version:'1.0.0'});
const transport=new StdioClientTransport({command:'node',args:['mcp/server.mjs']});
try{
  await client.connect(transport);
  const names=(await client.listTools()).tools.map(x=>x.name);
  if(!['open_video_review','get_video_review_notes','save_video_review_note'].every(x=>names.includes(x)))throw Error('missing tools');
  const opened=await client.callTool({name:'open_video_review',arguments:{projectDir:dir,filePath:file}});
  const data=opened.structuredContent;if(!data?.video?.sha256||!data.video.url)throw Error('bad widget payload');
  if(opened._meta?.['openai/outputTemplate'])throw Error('review editor still renders inline in the conversation');
  const ui=await client.readResource({uri:'ui://codex-video-review/review.html'});
  if(!ui.contents?.[0]?.text?.includes('视频打标'))throw Error('missing UI');
  checkScripts(ui.contents[0].text,2);
  const review=await fetch(data.reviewUrl);const page=await review.text();
  if(review.status!==200||!page.includes('__VIDEO_REVIEW_BOOTSTRAP__')||!page.includes('画面标记'))throw Error('review page failed');
  checkScripts(page,2);
  const capability=await fetch(data.sendCapabilityUrl);
  if(!capability.ok||typeof (await capability.json()).available!=='boolean')throw Error('send capability check failed');
  const res=await fetch(data.video.url,{headers:{range:'bytes=0-3'}});
  if(res.status!==206||(await res.text())!=='fake')throw Error('range stream failed');
  const note={id:'test-note-001',time:1.2,text:'测试圈选',marks:[{type:'box',points:[[.1,.1],[.5,.6]]}]};
  const args={projectDir:dir,filePath:file,sha256:data.video.sha256,note};
  await client.callTool({name:'save_video_review_note',arguments:args});
  await client.callTool({name:'save_video_review_note',arguments:args});
  const fromBrowser=await fetch(data.saveUrl,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(note)});
  if(!fromBrowser.ok||(await fromBrowser.json()).notes.length!==1)throw Error('browser save failed');
  const saved=(await client.callTool({name:'get_video_review_notes',arguments:{projectDir:dir,filePath:file}})).structuredContent;
  if(saved.notes.length!==1||saved.notes[0].marks[0].points[1][0]!==.5)throw Error('notes lost or duplicated');
  const disk=JSON.parse(await readFile(join(dir,'.codex-video-review',`${data.video.sha256}.json`),'utf8'));
  if(disk.notes.length!==1)throw Error('disk persistence failed');
  console.log('PASS tools, widget resource, review page, HTTP range, SHA binding, idempotent save, disk read');
  const origin=new URL(data.noteUrl).origin;
  const edited=await fetch(data.noteUrl,{method:'POST',headers:{origin,'content-type':'application/json'},body:JSON.stringify({action:'update',id:note.id,text:'已修改的测试标注'})});
  if(!edited.ok||(await edited.json()).notes[0].text!=='已修改的测试标注')throw Error('browser note update failed');
  if(!(await (await fetch(data.reviewUrl)).text()).includes('已修改的测试标注'))throw Error('review page reloaded stale note text');
  const updated=(await client.callTool({name:'update_video_review_note',arguments:{projectDir:dir,filePath:file,sha256:data.video.sha256,id:note.id,text:note.text}})).structuredContent;
  if(updated.notes[0].text!==note.text)throw Error('MCP note update failed');
  const second={...note,id:'test-note-002'};
  await client.callTool({name:'save_video_review_note',arguments:{...args,note:second}});
  const removed=await fetch(data.noteUrl,{method:'POST',headers:{origin,'content-type':'application/json'},body:JSON.stringify({action:'delete',id:second.id})});
  if(!removed.ok||(await removed.json()).notes.length!==1)throw Error('browser note delete failed');
  await client.callTool({name:'save_video_review_note',arguments:{...args,note:second}});
  const deleted=(await client.callTool({name:'delete_video_review_note',arguments:{projectDir:dir,filePath:file,sha256:data.video.sha256,id:second.id}})).structuredContent;
  if(deleted.notes.length!==1||deleted.notes[0].id!==note.id)throw Error('MCP note delete failed');
  console.log('PASS browser and MCP note update/delete preserve the other marks');
  const fakeBin=join(dir,'bin');await mkdir(fakeBin);
  const fakeCodex=join(fakeBin,'codex');
  await writeFile(fakeCodex,`#!${process.execPath}
const{appendFileSync,existsSync,writeFileSync}=require('node:fs');if(process.argv[2]==='queue'){const args=process.argv,thread=args[args.indexOf('--thread')+1],message=args[args.indexOf('--message')+1];if(args[args.indexOf('-m')+1]!=='gpt-6-sol'){console.error('wrong model');process.exit(1);}if(process.env.FAKE_QUEUE_UNAVAILABLE==='1'){console.error('readonly database');process.exit(1);}if(thread==='00000000-0000-4000-8000-000000000000'){console.error('no rollout found for thread id '+thread);process.exit(1);}if(!message.includes('1.200 秒')||!message.includes('box ')||(!message.includes('测试圈选')&&!message.includes('第二个区域'))){console.error('review notes missing from message');process.exit(1);}if(process.env.FAKE_REJECT_IMAGE==='1'&&args.includes('-i')){console.error('codex queue does not support image attachments');process.exit(1);}if(process.env.FAKE_CALL_LOG)appendFileSync(process.env.FAKE_CALL_LOG,'queue:'+thread+'\\n');if(process.env.FAKE_MESSAGE_LOG)appendFileSync(process.env.FAKE_MESSAGE_LOG,JSON.stringify(message)+'\\n');console.log('Queued');process.exit(0);}let buffer='';let experimental=false;process.stdin.on('data',chunk=>{buffer+=chunk;for(let end;(end=buffer.indexOf('\\n'))>=0;){const line=buffer.slice(0,end);buffer=buffer.slice(end+1);const request=JSON.parse(line);if(!request.id)continue;let result={};if(request.method==='initialize')experimental=request.params.capabilities?.experimentalApi===true;if(request.method==='thread/read')result={thread:{id:request.params.threadId,turns:[]}};if(request.method==='thread/resume'){if(!experimental||request.params.excludeTurns!==true)throw Error('lightweight resume required');if(process.env.FAKE_ACTIVE_ALWAYS==='1'||(process.env.FAKE_ACTIVE_ONCE_FILE&&!existsSync(process.env.FAKE_ACTIVE_ONCE_FILE))){if(process.env.FAKE_ACTIVE_ONCE_FILE)writeFileSync(process.env.FAKE_ACTIVE_ONCE_FILE,'1');process.stdout.write(JSON.stringify({id:request.id,error:{code:-32600,message:'thread '+request.params.threadId+' already has an active writer'}})+'\\n');continue;}result={thread:{id:request.params.threadId,turns:[]}};}if(request.method==='model/list')result={data:[{model:process.env.FAKE_UNSUPPORTED==='1'?'gpt-5.5':'gpt-6-sol',isDefault:true}]};if(request.method==='turn/start'){if(request.params.model!=='gpt-6-sol')throw Error('GPT-6 Sol required');result={turn:{id:'test-turn',status:'inProgress',items:[]}};if(process.env.FAKE_CALL_LOG)appendFileSync(process.env.FAKE_CALL_LOG,'start\\n');}process.stdout.write(JSON.stringify({id:request.id,result})+'\\n');if(request.method==='turn/start')setTimeout(()=>{if(process.env.FAKE_ASSISTANT==='1')process.stdout.write(JSON.stringify({method:'item/completed',params:{threadId:request.params.threadId,turnId:'test-turn',item:{type:'agentMessage',text:'已收到'}}})+'\\n');process.stdout.write(JSON.stringify({method:'turn/completed',params:{threadId:request.params.threadId,turn:{id:'test-turn',status:'completed',items:[]}}})+'\\n');},Number(process.env.FAKE_DELAY_MS||100));}});`);
  await chmod(fakeCodex,0o755);
  const withThread=new Client({name:'send-probe',version:'1.0.0'});
  const boundTransport=new StdioClientTransport({command:'node',args:['mcp/server.mjs'],env:{...process.env,PATH:`${fakeBin}:${process.env.PATH}`,CODEX_VIDEO_REVIEW_CODEX_BIN:fakeCodex,CODEX_THREAD_ID:'11111111-1111-4111-8111-111111111111'}});
  try{
    await withThread.connect(boundTransport);
    const bound=(await withThread.callTool({name:'open_video_review',arguments:{projectDir:dir,filePath:file}})).structuredContent;
    const sent=await fetch(bound.sendUrl,{method:'POST',headers:{origin:new URL(bound.sendUrl).origin}});
    if(!sent.ok||!(await sent.json()).state)throw Error('send did not queue a task turn');
    let state;for(let attempt=0;attempt<100;attempt++){await new Promise(resolve=>setTimeout(resolve,100));state=await (await fetch(bound.sendStatusUrl)).json();if(state.state==='failed')break;}
    if(state?.state!=='failed'||!state.error?.includes('没有 AI 回复'))throw Error('silent task completion was not reported as failure: '+JSON.stringify(state));
    console.log('PASS backend turn tracking reports a silent completion as failure');
  }finally{await withThread.close();}
  const answered=new Client({name:'answer-probe',version:'1.0.0'});
  const answerTransport=new StdioClientTransport({command:'node',args:['mcp/server.mjs'],env:{...process.env,PATH:`${fakeBin}:${process.env.PATH}`,CODEX_VIDEO_REVIEW_CODEX_BIN:fakeCodex,CODEX_THREAD_ID:'11111111-1111-4111-8111-111111111111',FAKE_ASSISTANT:'1'}});
  try{
    await answered.connect(answerTransport);
    const answerFile=join(dir,'answer.mp4');await writeFile(answerFile,'answer-video');
    const bound=(await answered.callTool({name:'open_video_review',arguments:{projectDir:dir,filePath:answerFile}})).structuredContent;
    await answered.callTool({name:'save_video_review_note',arguments:{projectDir:dir,filePath:answerFile,sha256:bound.video.sha256,note}});
    const sent=await fetch(bound.sendUrl,{method:'POST',headers:{origin:new URL(bound.sendUrl).origin}});
    if(!sent.ok)throw Error('answering task did not accept send');
    let state;for(let attempt=0;attempt<100;attempt++){await new Promise(resolve=>setTimeout(resolve,100));state=await (await fetch(bound.sendStatusUrl)).json();if(state.state==='completed')break;}
    if(state?.state!=='completed'||!state.assistantSeen)throw Error('assistant response was not confirmed');
    console.log('PASS backend turn tracking confirms an assistant response');
  }finally{await answered.close();}
  const callLog=join(dir,'send-calls.log');
  const dedupEnv={...process.env,PATH:`${fakeBin}:${process.env.PATH}`,CODEX_VIDEO_REVIEW_CODEX_BIN:fakeCodex,CODEX_THREAD_ID:'22222222-2222-4222-8222-222222222222',FAKE_ASSISTANT:'1',FAKE_DELAY_MS:'1000',FAKE_CALL_LOG:callLog};
  const clients=[new Client({name:'dedup-a',version:'1'}),new Client({name:'dedup-b',version:'1'})];
  try{
    await Promise.all(clients.map(c=>c.connect(new StdioClientTransport({command:'node',args:['mcp/server.mjs'],env:dedupEnv}))));
    const dedupFile=join(dir,'dedup.mp4');await writeFile(dedupFile,'dedup-video');
    const opened=await Promise.all(clients.map(c=>c.callTool({name:'open_video_review',arguments:{projectDir:dir,filePath:dedupFile}})));
    await clients[0].callTool({name:'save_video_review_note',arguments:{projectDir:dir,filePath:dedupFile,sha256:opened[0].structuredContent.video.sha256,note}});
    const urls=opened.map(x=>x.structuredContent.sendUrl);
    const first=await fetch(urls[0],{method:'POST',headers:{origin:new URL(urls[0]).origin}});
    if(!first.ok||!(await first.json()).state)throw Error('first cross-session send failed');
    const second=await fetch(urls[1],{method:'POST',headers:{origin:new URL(urls[1]).origin}});
    if(!second.ok||!(await second.json()).duplicate)throw Error('cross-session duplicate was not identified');
    let calls='';for(let attempt=0;attempt<100;attempt++){try{calls=await readFile(callLog,'utf8');if(calls.trim())break;}catch{}await new Promise(resolve=>setTimeout(resolve,100));}
    if(calls.trim().split('\n').length!==1)throw Error('duplicate started another task turn');
    console.log('PASS separate review pages submit the same note only once');
  }finally{await Promise.all(clients.map(c=>c.close()));}
  const unsupported=new Client({name:'unsupported-model-probe',version:'1'});
  try{
    await unsupported.connect(new StdioClientTransport({command:'node',args:['mcp/server.mjs'],env:{...dedupEnv,CODEX_THREAD_ID:'33333333-3333-4333-8333-333333333333',FAKE_UNSUPPORTED:'1'}}));
    const unsupportedFile=join(dir,'unsupported.mp4');await writeFile(unsupportedFile,'unsupported-video');
    const opened=(await unsupported.callTool({name:'open_video_review',arguments:{projectDir:dir,filePath:unsupportedFile}})).structuredContent;
    await unsupported.callTool({name:'save_video_review_note',arguments:{projectDir:dir,filePath:unsupportedFile,sha256:opened.video.sha256,note}});
    const capability=await (await fetch(opened.sendCapabilityUrl)).json();
    if(capability.available)throw Error('unsupported model was advertised as sendable');
    const response=await fetch(opened.sendUrl,{method:'POST',headers:{origin:new URL(opened.sendUrl).origin}});
    if(!response.ok)throw Error('unsupported model queue failed');
    let state;for(let attempt=0;attempt<100;attempt++){await new Promise(resolve=>setTimeout(resolve,100));state=await (await fetch(opened.sendStatusUrl)).json();if(state.state==='failed')break;}
    if(state?.state!=='failed'||!state.error?.includes('gpt-6-sol'))throw Error('unsupported model did not fail closed');
    console.log('PASS unsupported runtimes never silently downgrade the model');
  }finally{await unsupported.close();}
  const queued=new Client({name:'active-writer-probe',version:'1'});
  try{
    await queued.connect(new StdioClientTransport({command:'node',args:['mcp/server.mjs'],env:{...dedupEnv,CODEX_THREAD_ID:'44444444-4444-4444-8444-444444444444',FAKE_ACTIVE_ALWAYS:'1',FAKE_DELAY_MS:'100',FAKE_CALL_LOG:join(dir,'retry-calls.log'),FAKE_MESSAGE_LOG:join(dir,'retry-messages.log')}}));
    const queuedFile=join(dir,'queued.mp4');await writeFile(queuedFile,'queued-video');
    const opened=(await queued.callTool({name:'open_video_review',arguments:{projectDir:dir,filePath:queuedFile}})).structuredContent;
    await queued.callTool({name:'save_video_review_note',arguments:{projectDir:dir,filePath:queuedFile,sha256:opened.video.sha256,note}});
    const capability=await (await fetch(opened.sendCapabilityUrl)).json();
    if(!capability.available||capability.model!=='gpt-6-sol')throw Error('Codex queue was not recognized');
    const response=await fetch(opened.sendUrl,{method:'POST',headers:{origin:new URL(opened.sendUrl).origin}});
    if(!response.ok)throw Error('Codex queue did not accept the task request');
    let state;for(let attempt=0;attempt<100;attempt++){await new Promise(resolve=>setTimeout(resolve,100));state=await (await fetch(opened.sendStatusUrl)).json();if(state.state==='queued')break;}
    if(state?.state!=='queued'||state.delivery!=='codex-queue'||state.model!=='gpt-6-sol')throw Error('active task was not queued with GPT-6 Sol: '+JSON.stringify(state));
    const calls=await readFile(join(dir,'retry-calls.log'),'utf8');if(!calls.includes('queue:44444444-4444-4444-8444-444444444444'))throw Error('queued request targeted a different task');
    console.log('PASS active writer uses the Codex task queue with GPT-6 Sol');
    if(state.sentNoteIds?.length!==1||state.pendingNoteIds?.length!==0)throw Error('queued note was not marked submitted');
    const another={id:'test-note-other-region',time:1.2,text:'第二个区域单独修改',marks:[{type:'box',points:[[.65,.2],[.9,.7]]}]};
    await queued.callTool({name:'save_video_review_note',arguments:{projectDir:dir,filePath:queuedFile,sha256:opened.video.sha256,note:another}});
    state=await (await fetch(opened.sendStatusUrl)).json();
    if(state.sentNoteIds?.length!==1||state.pendingNoteIds?.[0]!==another.id)throw Error('new note was not separated from sent notes');
    const secondSend=await fetch(opened.sendUrl,{method:'POST',headers:{origin:new URL(opened.sendUrl).origin}});
    if(!secondSend.ok)throw Error('second region could not be sent separately');
    for(let attempt=0;attempt<100;attempt++){await new Promise(resolve=>setTimeout(resolve,100));state=await (await fetch(opened.sendStatusUrl)).json();if(state.sentNoteIds?.length===2)break;}
    if(state.sentNoteIds?.length!==2||state.pendingNoteIds?.length!==0)throw Error('second region was not marked submitted');
    const messages=(await readFile(join(dir,'retry-messages.log'),'utf8')).trim().split('\n').map(JSON.parse);
    if(messages.length!==2||messages[1].includes('测试圈选')||!messages[1].includes('第二个区域')||!messages[1].includes('box 65–90% 横向'))throw Error('second send did not isolate its own text and region');
    console.log('PASS submitted and pending notes stay separate; same-time regions retain distinct text and coordinates');
    const reopened=new Client({name:'other-thread-probe',version:'1'});
    try{
      await reopened.connect(new StdioClientTransport({command:'node',args:['mcp/server.mjs'],env:{...dedupEnv,CODEX_THREAD_ID:'66666666-6666-4666-8666-666666666666'}}));
      const other=(await reopened.callTool({name:'open_video_review',arguments:{projectDir:dir,filePath:queuedFile}})).structuredContent;
      const previous=await (await fetch(other.sendStatusUrl)).json();
      if(previous.sentNoteIds?.length!==2||previous.pendingNoteIds?.length!==0||previous.threadId!=='44444444-4444-4444-8444-444444444444')throw Error('reopened task lost the previous send receipts');
    }finally{await reopened.close();}
    console.log('PASS a new task still recognizes the video notes submitted from the earlier task');
  }finally{await queued.close();}
  const realFile=join(dir,'frame-test.mp4');
  execFileSync('ffmpeg',['-hide_banner','-loglevel','error','-f','lavfi','-i','color=c=white:s=640x360:d=2','-y',realFile]);
  const imageClient=new Client({name:'image-probe',version:'1'});
  try{
    await imageClient.connect(new StdioClientTransport({command:'node',args:['mcp/server.mjs'],env:{...dedupEnv,CODEX_THREAD_ID:'55555555-5555-4555-8555-555555555555',FAKE_ACTIVE_ALWAYS:'1',FAKE_REJECT_IMAGE:'1'}}));
    const opened=(await imageClient.callTool({name:'open_video_review',arguments:{projectDir:dir,filePath:realFile}})).structuredContent;
    await imageClient.callTool({name:'save_video_review_note',arguments:{projectDir:dir,filePath:realFile,sha256:opened.video.sha256,note}});
    const sent=await fetch(opened.sendUrl,{method:'POST',headers:{origin:new URL(opened.sendUrl).origin}});
    if(!sent.ok)throw Error('image review send failed');
    let state;for(let attempt=0;attempt<100;attempt++){await new Promise(resolve=>setTimeout(resolve,100));state=await (await fetch(opened.sendStatusUrl)).json();if(['queued','failed'].includes(state.state))break;}
    if(state?.state!=='queued')throw Error('text-only queue failed: '+JSON.stringify(state));
    console.log('PASS queued review message includes note text and mark coordinates without image arguments');
  }finally{await imageClient.close();}
}finally{await client.close();await rm(dir,{recursive:true,force:true});}
