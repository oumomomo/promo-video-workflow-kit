#!/usr/bin/env python3
import argparse,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent/'skills/video-production-tools'
p=argparse.ArgumentParser(description='产品片段卡、自动视听候选分析、配音、音乐计划、生产账本与局改保护')
p.add_argument('--library');p.add_argument('tool',choices=['contract','cards','analyze','voice','music','ledger','archive-audit','evidence']);a,rest=p.parse_known_args()
paths={'contract':'scripts/contract.py','cards':'scripts/product_reference.py','analyze':'analysis/pipeline.py','voice':'voice/scripts/voiceover_cli.py','music':'scripts/music.py','ledger':'scripts/ledger.py','archive-audit':'scripts/archive_state.py','evidence':'scripts/check_shot_evidence.py'}
env=dict(os.environ)
if a.library:env['VIDEO_WORKFLOW_LIBRARY']=str(Path(a.library).expanduser().resolve())
raise SystemExit(subprocess.call([sys.executable,str(ROOT/paths[a.tool]),*rest],env=env))
