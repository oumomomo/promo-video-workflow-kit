"""Readable automatic evidence report; no manual annotations required."""
import html
import os
from pathlib import Path
from urllib.parse import quote

LABELS = {
    'description':'描述','instruments':'乐器／音色','rhythm':'节奏','entrance':'进入方式',
    'ending':'结束方式','present':'是否有人声','timbre':'音色','pace':'语速',
    'pauses':'停顿','emphasis':'重音','composition':'构图','action':'动作',
    'transition':'过渡','evidenceDescription':'画面依据','category':'类型',
    'functionCandidate':'用途候选','reason':'待辨认原因','uncertainty':'不确定性',
    'visualTime':'画面时间（片段内秒）','audioTime':'声音时间（片段内秒）',
}
def esc(x):
    return html.escape(str(x))
def value(x):
    if x is None:return '未判断'
    if x is True:return '有'
    if x is False:return '无'
    if isinstance(x,list):return '；'.join(value(v) for v in x) or '未检出明确候选'
    if isinstance(x,dict):return '；'.join(f'{LABELS.get(k,k)}：{value(v)}' for k,v in x.items())
    return str(x)
def render(out, data):
    out=Path(out)
    source=quote(os.path.relpath(data['source'],out),safe='/')
    blocks=[]
    classified={row['id']:row for part in data.get('jev',{}).get('results',[]) for row in part.get('rows',[])}
    dimension_labels={'scriptRole':'脚本作用','visualForm':'画面形式','motionRole':'动作作用','soundRole':'声音作用','reviewIssue':'主要复核疑点'}
    for wi,w in enumerate(data['windows']):
        content=[]
        for key,label in [('visual','画面与动效'),('bgm','BGM · 配乐'),('sfx','SFX · 独立音效'),('voiceover','口播'),('unclassified','待辨认声音'),('sync','音画关系候选')]:
            entries=w.get('analysis',{}).get(key)
            entries=entries if isinstance(entries,list) else [entries]
            rows=[]
            for ri,e in enumerate(entries):
                dimensions=classified.get(f'w{wi}-{key}-{ri}',{}).get('analysis',{}).get('dimensions',{})
                tags=''
                for name,d in dimensions.items():
                    candidate=f'（模型候选：{d.get("suggestedLabel",d.get("choice"))}）' if d.get('choice') and d.get('effectiveChoice')!=d.get('choice') else ''
                    tags+=f'<dt>{esc(dimension_labels.get(name,name))}</dt><dd>{esc(d.get("label",d.get("effectiveChoice","unknown")))}{esc(candidate)}'+(' · 待复核' if d.get('needsReview') else '')+'</dd>'
                tags='<details><summary>描述分类建议 · 未核验原片</summary><dl>'+tags+'</dl></details>' if tags else ''
                if isinstance(e,dict):
                    timing=''
                    if isinstance(e.get('start'),(float,int)) and isinstance(e.get('end'),(float,int)):
                        a=w['start']+e['start'];b=w['start']+e['end']
                        timing=f'<button data-time="{a}">{a:.2f}–{b:.2f}s · 定位原片</button>'
                    rows.append('<div class="entry">'+timing+'<dl>'+''.join(f'<dt>{esc(LABELS.get(k,k))}</dt><dd>{esc(value(v))}</dd>' for k,v in e.items() if k not in ['start','end','status'])+'</dl>'+tags+'</div>')
                elif e is not None:rows.append('<p>'+esc(value(e))+'</p>'+tags)
            content.append('<section><h3>'+label+'</h3>'+(''.join(rows) or '<p class="muted">未检出明确候选</p>')+'</section>')
        issue='<p class="issue">'+esc(w.get('error','分段尚未完成'))+'</p>' if w['status'] not in ['candidate','no_audio'] else ''
        warning='<p class="muted">校验记录：'+esc('；'.join(w.get('warnings',[])))+'</p>' if w.get('warnings') else ''
        blocks.append(f'<article><h2>{w["start"]:.2f}–{w["end"]:.2f} 秒</h2>'+issue+warning+''.join(content)+'</article>')
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>自动拉片分类报告</title><style>
body{margin:0;background:#f5f4ef;color:#24382c;font:16px/1.7 system-ui,sans-serif}main{max-width:1000px;margin:auto;padding:24px}video{width:100%;max-height:58vh;background:#111}article{background:white;border:1px solid #dadfd8;padding:24px;margin:24px 0}section{border-top:1px solid #e1e4df;padding:12px 0}dl{margin:12px 0}dt{color:#617268;font-size:13px}dd{margin:0 0 10px;overflow-wrap:anywhere}.entry{padding:12px 0}.muted{color:#64716b}.issue{color:#953e28}button{border:1px solid #acc0b0;background:#f2f7f1;padding:8px 12px;color:#275c43;border-radius:6px;cursor:pointer}a{color:#275c43}h3{font-size:18px}header{margin-bottom:24px}</style><main><header><a href="../index.html">← 全部素材</a><h1>自动拉片 · 分类报告</h1><p><a href="evidence.html">查看逐帧时间证据与音效对照试听 →</a></p><p>画面、BGM、音效、口播分别记录。下方区间按钮使用原片时间；描述和时间都是模型候选。播放的是原片混音，并非分离后的音效。</p>'''
    status_label={'completed_with_uncertainty':'自动分析已完成，保留疑点','incomplete':'尚未完成'}.get(data['executionStatus'],data['executionStatus'])
    page+=f'<p>执行状态：{esc(status_label)}</p><video id="video" controls preload="metadata" src="{source}"></video></header>'+''.join(blocks)
    page+='''</main><script>document.addEventListener('click',e=>{let b=e.target.closest('[data-time]');if(!b)return;let v=document.getElementById('video');v.currentTime=Number(b.dataset.time);v.scrollIntoView({behavior:'smooth',block:'center'});});</script></html>'''
    (out/'index.html').write_text(page)
