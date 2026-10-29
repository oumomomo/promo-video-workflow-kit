import importlib.util,os,json,hashlib
from pathlib import Path
SKILL=Path(__file__).resolve().parents[1]
REF=SKILL.parent/'video-reference-kit/scripts/video_ref.py'
spec=importlib.util.spec_from_file_location('workflow_ref',REF);ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
def library():return ref.Library(os.environ.get('VIDEO_WORKFLOW_LIBRARY') or None)
def gateway(*args,body=None):return library().call(*args,request=body)
def submit_analysis(out,source,digest):
 lib=library();record=lib.call('register','--file',str(source),'--kind','reference_video','--title',source.stem)
 ref.PRODUCER='automatic-reference-analysis'
 docs=[{'key':p.name,'body':p.read_text(),'format':p.suffix} for p in sorted(out.iterdir()) if p.name in ['analysis.json','REPORT.md','precision.json','sound-reuse.json','HANDOFF.md']]
 return ref.submit(lib,record['id'],'analysis',docs)
