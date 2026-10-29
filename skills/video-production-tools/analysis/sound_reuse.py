"""Reference sound cues -> eligible library alternatives, never claimed originals."""
import json, re, shutil
from pathlib import Path
from pipeline import read, run, save, sha

FAMILIES={
 'click':('click','tap','tick','点击','轻触','敲击','输入'),
 'whoosh':('whoosh','swoosh','swish','掠过','呼啸','划过','扫过'),
 'impact':('impact','thud','hit','撞击','冲击','重击'),
 'riser':('riser','rise','上升','渐强'),
 'glitch':('glitch','digital distortion','故障','失真'),
 'chime':('chime','ding','bell','铃声','叮','提示音'),
}

def families(text):
    text=text.lower()
    return [key for key,terms in FAMILIES.items() if any((re.search(r'(?<![a-z])'+re.escape(t)+r'(?![a-z])',text) if t.isascii() else t in text) for t in terms)]

def eligible_assets():
    # Source clips remain available for listening; no private audio library lookup.
    return []

def rank(event,assets):
    cue=' '.join(str(event.get(k,'')) for k in ['description','category','functionCandidate','visualContext']).lower()
    wanted=set(families(' '.join(str(event.get(k,'')) for k in ['description','category','functionCandidate'])))
    found=[]
    for a in assets:
        if not a.get('aiEligible') or not a.get('hashMatches') or a.get('kind')!='sound_effect':continue
        text=' '.join(str(v) for v in [a.get('title'),a.get('category'),a.get('role'),*(a.get('tags') or [])] if v)
        requirements=[('camera','shutter','相机','快门'),('glass','玻璃'),('sand','砂','沙'),('water','liquid','水','流体'),('wood','木'),('metal','金属'),('cloth','fabric','布料'),('door','门')]
        if any(any(t in text.lower() for t in group) and not any(t in cue for t in group) for group in requirements):continue
        overlap=wanted & set(families(text))
        if not overlap:continue
        # Role/type retrieval only, never waveform-identical or perceptually verified.
        score=len(overlap)*10+(1 if a.get('speechSafety')=='high' else 0)
        found.append((score,a['id'],a,sorted(overlap)))
    return sorted(found,key=lambda x:(-x[0],x[1]))[:3]

def build(source,out,data,assets):
    out=Path(out);folder=out/'sound-reuse';folder.mkdir(exist_ok=True)
    previews=folder/'previews';previews.mkdir(exist_ok=True)
    cards=[]
    for w in data['windows']:
        for i,e in enumerate(w.get('analysis',{}).get('sfx',[])):
            start=w['start']+e['start'];end=w['start']+e['end'];key=f'sfx-{w["start"]}-{i}'
            context_start=max(0,start-.3);context_end=min(data['duration'],end+.4)
            clip=folder/f'{key}-mixed.wav'
            if not clip.exists():run(['ffmpeg','-v','error','-y','-ss',context_start,'-i',source,'-t',context_end-context_start,'-vn','-c:a','pcm_s16le',clip])
            alternatives=[]
            event=dict(e,visualContext=' '.join(str(v.get('composition',''))+' '+str(v.get('action','')) for v in w.get('analysis',{}).get('visual',[]) if v['start']<e['end'] and v['end']>e['start']))
            for score,aid,a,matched in rank(event,assets):
                original=Path(a['localPath']);digest=sha(original)
                if digest!=a['actualSha256']:raise ValueError('audio library changed during validation')
                preview=previews/(digest+original.suffix)
                if not preview.exists() or sha(preview)!=digest:shutil.copy2(original,preview)
                alternatives.append({'assetId':aid,'storedVersion':a.get('storedVersion'),'title':a['title'],
                    'sourceFile':str(original),'sha256':digest,'preview':str(preview.relative_to(out)),
                    'matchMethod':'type_and_function_retrieval_not_acoustic_match','matchedFamilies':matched,
                    'rights':a.get('rights'),'mixDefault':a.get('mixDefault'),
                    'disabledScenes':a.get('disabledScenes',[]),'reusePolicy':a.get('reusePolicy'),
                    'selectionStatus':'suggested_not_adopted'})
            cards.append({'id':key,'start':start,'end':end,'description':e.get('description'),
                'status':'model_sound_candidate','referenceAudio':str(clip.relative_to(out)),
                'contextStart':context_start,'contextEnd':context_end,'referenceType':'original_mixed_audio',
                'alternatives':alternatives,'reuseStatus':'alternatives_available' if alternatives else 'no_type_match',
                'sourceOriginalSfxIdentified':False})
    result={'sourceSha256':data['sourceSha256'],'catalogSource':'existing unified DB via validated audio adapter',
            'eligibleLibraryCount':len(assets),'cards':cards,'stemSeparationPerformed':False,
            'limitations':['匹配的是类型与用途，不是识别出作者实际使用的音效文件。','参考试听包含BGM、口播与音效的原混音。','替代音效通过现有库规则和哈希校验，仍需按画面及禁用场景选择。']}
    save(out/'sound-reuse.json',result)
    return result
