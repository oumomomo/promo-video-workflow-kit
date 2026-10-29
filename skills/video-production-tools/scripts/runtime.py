import importlib.util,os,json,hashlib
from pathlib import Path
SKILL=Path(__file__).resolve().parents[1]
REF=SKILL.parent/'video-reference-kit/scripts/video_ref.py'
spec=importlib.util.spec_from_file_location('workflow_ref',REF);ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
def library():return ref.Library(os.environ.get('VIDEO_WORKFLOW_LIBRARY') or None)
def gateway(*args,body=None):return library().call(*args,request=body)
def lookup_source(source,require_library=False):
 # Independent evidence preparation need not create a database. Existing/shared
 # configuration, explicit selection and protected workspaces must never fall back.
 shared=ref.shared_configuration()
 required=(require_library or bool(shared) or bool(os.environ.get('VIDEO_WORKFLOW_LIBRARY'))
           or ref.protected_workspace(Path.cwd()) or ref.protected_workspace(source))
 if required:return library().call('lookup','--file',str(source))
 return {'match':'not_checked','reason':'standalone_without_configured_library; no_database_created'}
def submit_analysis(out,source,digest):
 lib=library();record=lib.call('register','--file',str(source),'--kind','reference_video','--title',source.stem)
 ref.PRODUCER='automatic-reference-analysis'
 docs=[{'key':p.name,'body':p.read_text(),'format':p.suffix} for p in sorted(out.iterdir()) if p.name in ['analysis.json','REPORT.md','precision.json','sound-reuse.json','HANDOFF.md']]
 return ref.submit(lib,record['id'],'analysis',docs)
