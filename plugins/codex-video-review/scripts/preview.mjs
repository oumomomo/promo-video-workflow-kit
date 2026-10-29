import {fileURLToPath} from 'node:url';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';

const [projectDir,filePath]=process.argv.slice(2);
if(!projectDir||!filePath)throw new Error('Usage: node scripts/preview.mjs <projectDir> <filePath>');
const client=new Client({name:'video-review-preview',version:'1.0.0'});
await client.connect(new StdioClientTransport({command:'node',args:[fileURLToPath(new URL('../mcp/server.mjs',import.meta.url))],env:{...process.env,CODEX_THREAD_ID:process.env.CODEX_THREAD_ID||''}}));
const result=await client.callTool({name:'open_video_review',arguments:{projectDir,filePath}});
if(result.isError)throw new Error(result.content?.[0]?.text||'Open failed');
process.stdout.write(result.structuredContent.reviewUrl+'\n');
process.on('SIGINT',async()=>{await client.close();process.exit(0);});
await new Promise(()=>{});
