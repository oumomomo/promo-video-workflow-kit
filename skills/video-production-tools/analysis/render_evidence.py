import html
from pathlib import Path

def esc(v):return html.escape(str(v))

def render(out, precision, reuse):
    out=Path(out)
    head='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>时间证据与音效复用</title><style>
body{font:16px/1.7 system-ui,sans-serif;margin:0;background:#f5f4ef;color:#24382c}main{max-width:1080px;margin:auto;padding:24px}article,details{padding:20px;background:white;border:1px solid #dce2d9;margin:18px 0;min-width:0}a{color:#275c43}summary{cursor:pointer;font-weight:600}audio{width:100%;max-width:420px}img{max-width:100%;height:auto}figure{margin:0}figcaption,.muted{color:#66766a;font-size:14px}.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}p{overflow-wrap:anywhere}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:9px;border-bottom:1px solid #ddd;text-align:left}h2{margin-top:36px}@media(max-width:700px){.pair{grid-template-columns:1fr}main{padding:16px}}</style><main><a href="index.html">← 分类报告</a><h1>时间证据与音效复用</h1><p>相邻帧给出真实帧时间；音频只测混音中的瞬态。两者靠近说明时间接近，不能据此证明是独立音效或创作上的卡点。</p>'''
    cuts=[]
    for c in precision['cuts']:
        cuts.append(f'<details><summary>{c["afterTime"]:.3f}s · 画面变化候选</summary><p>相邻帧：{c["frameBefore"]} → {c["frameAfter"]}；间隔 {c["frameIntervalSeconds"]*1000:.2f}ms。{esc(c["notProof"])}</p><div class="pair"><figure><img loading="lazy" src="{esc(c["beforeImage"])}"><figcaption>{c["beforeTime"]:.3f}s · 变化前</figcaption></figure><figure><img loading="lazy" src="{esc(c["afterImage"])}"><figcaption>{c["afterTime"]:.3f}s · 变化后</figcaption></figure></div></details>')
    page=head+f'<h2>逐帧时间证据 · {len(cuts)} 处</h2>'+''.join(cuts)
    page+='<h2>音画时间对照</h2><p>“无局部证据”也可能是缓慢起音或镜头内动作；并不自动推翻模型描述。模型时间不会被静默吸附到最近瞬态。</p><table><thead><tr><th>模型画面时间</th><th>实测画面变化</th><th>实测混音瞬态</th><th>差值</th></tr></thead><tbody>'
    def stamp(x):return f'{x:.3f}s' if x is not None else '无局部证据'
    for e in precision['syncChecks']:
        delta=f'{e["measuredDeltaMs"]:+.1f}ms' if e['measuredDeltaMs'] is not None else '未计算'
        page+=f'<tr><td>{e["modelVisualTime"]:.2f}s</td><td>{stamp(e["measuredVisualChange"])}</td><td>{stamp(e["measuredSoundTransient"])}</td><td>{delta}</td></tr>'
    page+='</tbody></table><h2>参考声音与替代音效</h2><p>左侧听原片混音，右侧听库里的独立音效。替代建议按类型与用途检索，未认定为原作者用的同一文件，也未自动采用。</p>'
    checks={e['id']:e for e in precision['sfxChecks']}
    for c in reuse['cards']:
        check=checks.get(c['id'],{});alternatives=[]
        for a in c['alternatives']:
            alternatives.append(f'<section><h3>{esc(a["title"])}</h3><audio controls preload="none" src="{esc(a["preview"])}"></audio><p class="muted">匹配类型：{esc(" / ".join(a["matchedFamilies"]))}；授权记录：{esc(a["rights"].get("license"))}；默认增益：{esc(a.get("mixDefault",{}).get("gainDb"))} dB</p><p class="muted">禁用场景：{esc("；".join(a["disabledScenes"]))}</p></section>')
        page+=f'<article><h3>{c["start"]:.2f}–{c["end"]:.2f}s · 音效候选</h3><p>{esc(c["description"])}</p><div class="pair"><section><h3>原片混音 · 仅作证据</h3><audio controls preload="none" src="{esc(c["referenceAudio"])}"></audio><p class="muted">附近混音瞬态：{stamp(check.get("measuredNearbyTransient"))}。试听范围 {c["contextStart"]:.2f}–{c["contextEnd"]:.2f}s。</p></section><section>'+(''.join(alternatives) or '<p>库中未找到类型明确的替代候选，保留缺项。</p>')+'</section></div></article>'
    (out/'evidence.html').write_text(page+'</main></html>')
    md='# 复用交接 · 自动候选\n\n来源 SHA256：'+reuse['sourceSha256']+'\n\n本文件提供参考线索和替代音效，不表示已采用或完整精拉已验收。画面继承/调整需要结合目标项目；本次不改写脚本或启动制作。\n\n'
    for c in reuse['cards']:
        md+=f'## {c["start"]:.2f}–{c["end"]:.2f}s\n\n参考声音：{c["description"]}\n\n原片混音证据：[{c["id"]}]({c["referenceAudio"]})\n\n'
        for a in c['alternatives']:
            md+=f'- 替代候选：{a["title"]}；资产 `{a["assetId"]}`；版本 `{a["storedVersion"]}`；SHA256 `{a["sha256"]}`。禁用场景：'+ '；'.join(a['disabledScenes'])+'。\n'
        if not c['alternatives']:md+='- 暂无明确替代候选，不自动填充。\n'
    (out/'HANDOFF.md').write_text(md)
