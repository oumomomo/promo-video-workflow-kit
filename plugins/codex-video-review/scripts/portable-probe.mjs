import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
import {mkdtemp,mkdir,readFile,writeFile,appendFile,rm,symlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const dir=await mkdtemp(join(tmpdir(),'portable-review-'));const project=join(dir,'project');await mkdir(project);
const file=join(project,'test.mp4');const server=fileURLToPath(new URL('../mcp/server.mjs',import.meta.url));
const create=async()=>{const c=new Client({name:'portable-isolated-test',version:'1'});await c.connect(new StdioClientTransport({command:process.execPath,args:[server],cwd:tmpdir(),env:{...process.env,CODEX_THREAD_ID:''}}));return c;};
let client;
try{
 execFileSync('ffmpeg',['-v','error','-f','lavfi','-i','testsrc2=s=320x180:r=10:d=2','-c:v','libx264','-y',file]);
 client=await create();const args={projectDir:project,filePath:file};const opened=await client.callTool({name:'open_video_review',arguments:args});if(opened.isError)throw Error(JSON.stringify(opened));const data=opened.structuredContent;
 const response=await fetch(data.video.url,{headers:{Range:'bytes=0-31'}});if(response.status!==206||!Buffer.from(await response.arrayBuffer()).equals((await readFile(file)).subarray(0,32)))throw Error('media bytes differ');
 const page=await(await fetch(data.reviewUrl)).text();if(!page.includes('画面标记')||!page.includes('保存这处标注'))throw Error('missing review controls');
 const note={id:'agent-test-portable',time:.7,text:'技术夹具标注，不是用户反馈',marks:[{type:'box',points:[[.1,.2],[.7,.8]]}]};
 const saved=await client.callTool({name:'save_video_review_note',arguments:{...args,sha256:data.video.sha256,note}});if(saved.isError)throw Error('save failed');
 await client.close();client=await create();const got=await client.callTool({name:'get_video_review_notes',arguments:args});if(got.structuredContent?.notes?.[0]?.text!==note.text)throw Error('notes not recovered after restart');
 const outside=join(dir,'outside.mp4');await writeFile(outside,await readFile(file));const escaped=await client.callTool({name:'open_video_review',arguments:{projectDir:project,filePath:outside}});if(!escaped.isError)throw Error('outside video accepted');
 await symlink(outside,join(project,'escape.mp4'));const linked=await client.callTool({name:'open_video_review',arguments:{projectDir:project,filePath:join(project,'escape.mp4')}});if(!linked.isError)throw Error('symlink escape accepted');
 await appendFile(file,Buffer.from('changed-fixture'));const changed=await client.callTool({name:'save_video_review_note',arguments:{...args,sha256:data.video.sha256,note}});if(!changed.isError)throw Error('stale hash accepted');
 const fresh=await client.callTool({name:'get_video_review_notes',arguments:args});if(fresh.structuredContent.notes.length!==0)throw Error('notes crossed hashes');
 console.log('PASS real MP4 Range bytes, review HTML controls, start from unrelated cwd, persisted marks after process restart, project and symlink boundaries, stale SHA rejection, changed-file note isolation');
}finally{await client?.close();await rm(dir,{recursive:true,force:true});}
