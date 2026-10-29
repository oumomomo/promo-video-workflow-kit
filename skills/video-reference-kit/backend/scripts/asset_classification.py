"""Evidence-backed historical classification; approval/rights are never modified."""
import json,re
from pathlib import Path
HISTORY=json.loads((Path(__file__).resolve().parents[1]/'src/asset-library/historical-classification.json').read_text())
KINDS={'analysis_document':'拆解与研究文档','audio':'音频素材','fact':'产品事实','font':'字体素材','frame_evidence':'拆解与验收帧','image':'图片素材','method':'创作方法','motion_capability':'动效配方','music_track':'背景音乐','project':'项目工程','sound_effect':'音效','video':'项目视频素材'}

def infer(rid,title,kind,metadata):
    known=HISTORY.get(rid)
    if known and known['title']==title:
        return known['category'],{'version':1,'level':'content','basis':known['basis'],'subtype':known['subtype'],'sources':known['sources'],'evidence':known['focus'],'tags':[known['subtype']]}
    if kind in KINDS:
        return KINDS[kind],{'version':1,'level':'asset_role','basis':'已有资产类型字段：'+kind,'tags':[],'note':'按素材角色归类；未推断画面内容、声音风格或授权状态'}
    return '待分类',{'version':1,'level':'unknown','basis':'缺少可确定内容用途的证据','tags':[]}

def enrich(metadata,classification):
    result=dict(classification);tags=list(result.get('tags') or [])
    if result.get('subtype'):tags.append(result['subtype'])
    focus='；'.join(metadata.get('focus',[]))
    focus=re.sub(r'[^；。;]*(?:没有|不采用|不使用|而非)[^；。;]*','',focus)
    for tag,words in {'动态排版':['字卡','字形','排版'],'对象接力':['接力','共享对象'],'运镜':['运镜','推近','拉远'],'界面操作':['输入框','光标','点击'],'数据可视化':['图表','数值','指标'],'材质变化':['材质','液态','燃烧'],'拼贴构图':['拼贴','多区']}.items():
        if any(w in focus for w in words):tags.append(tag)
    result['tags']=sorted(set(tags));return result
