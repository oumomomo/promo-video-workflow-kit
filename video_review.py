#!/usr/bin/env python3
"""Portable bundled video-review entrypoint. Never changes host MCP configuration."""
import argparse,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PLUGIN=ROOT/'plugins/codex-video-review'
def main():
 p=argparse.ArgumentParser(description='随包视频打标：检查、安装依赖、生成连接配置或临时打开；不修改宿主设置')
 sub=p.add_subparsers(dest='action',required=True)
 sub.add_parser('doctor');s=sub.add_parser('setup');s.add_argument('--offline',action='store_true')
 sub.add_parser('config')
 o=sub.add_parser('open');o.add_argument('--project',required=True);o.add_argument('--file',required=True)
 a=p.parse_args();node=shutil.which('node');npm=shutil.which('npm')
 if a.action=='doctor':
  version=subprocess.check_output([node,'--version'],text=True).strip() if node else None
  installed=(PLUGIN/'node_modules/@modelcontextprotocol/sdk').is_dir() and (PLUGIN/'node_modules/@modelcontextprotocol/ext-apps').is_dir() and (PLUGIN/'node_modules/zod').is_dir()
  print(json.dumps({'node':node,'nodeVersion':version,'node20OrNewer':bool(version and int(version[1:].split('.')[0])>=20),'npm':npm,'dependenciesInstalled':installed,'browserBundleIncluded':(PLUGIN/'dist/widget.js').is_file(),'autoSend':'depends_on_host_thread_bridge_and_Codex; not_guaranteed','privateMediaIncluded':False},ensure_ascii=False,indent=2));return
 if not node:raise ValueError('请先安装Node.js 20+')
 if a.action=='setup':
  if not npm:raise ValueError('请先安装npm')
  subprocess.run([npm,'ci','--ignore-scripts',*(['--offline'] if a.offline else [])],cwd=PLUGIN,check=True);return
 if a.action=='config':
  print(json.dumps({'mcpServers':{'codex_video_review':{'command':node,'args':[str(PLUGIN/'mcp/server.mjs')],'cwd':str(PLUGIN)}}},ensure_ascii=False,indent=2));return
 project=Path(a.project).expanduser().resolve();file=Path(a.file).expanduser().resolve()
 if not file.is_file() or not file.is_relative_to(project):raise ValueError('视频必须在项目目录内并存在')
 subprocess.run([node,str(PLUGIN/'scripts/preview.mjs'),str(project),str(file)],cwd=PLUGIN,check=True)
if __name__=='__main__':
 try:main()
 except (ValueError,subprocess.CalledProcessError) as e:print(str(e),file=sys.stderr);sys.exit(1)
