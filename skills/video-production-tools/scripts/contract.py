"""Visual direction contract: structural completeness, not automated aesthetic approval."""
import argparse,json
from pathlib import Path
from runtime import ref
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('action',choices=['init','check']);a=p.parse_args();root=a.project.resolve();file=root/'workflow/visual-reference-contract.json';plan=json.loads((root/'workflow/plan.json').read_text())
if a.action=='init':
 if file.exists():raise SystemExit('已有视觉合同，不覆盖')
 data=json.loads((Path(__file__).resolve().parents[1]/'references/visual-contract.template.json').read_text());data['shotBindings']=[{'shotId':s['id'],'inherit':[],'change':[],'reject':[],'visualEvent':s.get('event',''),'sourceAssetIds':[]} for s in plan['shots']];ref.write(file,data);print(json.dumps({'state':'draft','path':str(file),'approved':False}))
else:
 d=json.loads(file.read_text());errors=[];world=d.get('visualWorld',{});policy=d.get('referencePolicy',{})
 if not world.get('continuityMechanism') or not world.get('colorSource',{}).get('evidence'):errors.append('缺整片连续性或颜色依据')
 if not world.get('sourceMaterials') and not policy.get('originalReason'):errors.append('缺原材料或本次原创依据')
 bindings=d.get('shotBindings',[]);ids=[x.get('shotId') for x in bindings]
 if len(ids)!=len(set(ids)) or set(ids)!=set(s['id'] for s in plan['shots']):errors.append('视觉合同未逐镜覆盖当前分镜')
 for b in bindings:
  if not b.get('visualEvent') or not all(isinstance(b.get(k),list) for k in ['inherit','change','reject','sourceAssetIds']):errors.append('逐镜职责或继承/调整/拒绝字段缺失')
 print(json.dumps({'passed':not errors,'errors':errors,'meaning':'字段完整性；不证明原片行为、审美或真人批准'},ensure_ascii=False,indent=2));raise SystemExit(bool(errors))
