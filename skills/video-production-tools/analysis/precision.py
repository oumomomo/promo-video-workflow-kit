"""Local frame and sound timing evidence. Measurements are never semantic approval."""
import json, subprocess
from pathlib import Path
import numpy as np
from pipeline import read, run, save

VERSION='local-precision-v1'

def nearest(values, target, radius):
    if not values:return None
    value=min(values,key=lambda v:abs(v-target))
    return value if abs(value-target)<=radius else None

def transient_times(samples, sample_rate):
    if not len(samples):return [],[]
    hop=max(1,round(sample_rate*.01));size=hop*4
    # Analyze channel power, never summing opposite phases into silence.
    powers=[];spectra=[];times=[]
    for i in range(0,len(samples)-size+1,hop):
        chunk=samples[i:i+size]
        powers.append(float(np.sqrt(np.mean(chunk**2))))
        spectra.append(np.mean(np.abs(np.fft.rfft(chunk*np.hanning(size)[:,None],axis=0)),axis=1))
        times.append((i+size/2)/sample_rate)
    if len(spectra)<3:return [],powers
    flux=np.maximum(np.diff(spectra,axis=0),0).sum(axis=1)
    candidates=[]
    for j in range(1,len(flux)-1):
        neighbourhood=flux[max(0,j-25):min(len(flux),j+26)]
        baseline=float(np.median(neighbourhood));spread=float(np.median(np.abs(neighbourhood-baseline)))
        if flux[j]>max(baseline+3*spread,1e-7) and flux[j]>=flux[j-1] and flux[j]>flux[j+1]:
            t=times[j+1]
            if not candidates or t-candidates[-1]>=.04:candidates.append(round(t,5))
    return candidates,powers

def extract_selected_frames(source,indices,frames_dir):
    # Bound expression depth: long sums overflow FFmpeg's expression parser.
    for offset in range(0,len(indices),64):
        chunk=indices[offset:offset+64]
        expr='+'.join(f'eq(n,{i})' for i in chunk)
        run(['ffmpeg','-v','error','-y','-i',source,'-vf',f"select='{expr}',scale=480:-2",'-fps_mode','passthrough','-start_number',offset+1,frames_dir/'frame-%05d.jpg'])

def build(source,out,data):
    out=Path(out);folder=out/'precision';folder.mkdir(exist_ok=True)
    cache=folder/'measurements.json'
    if cache.exists() and read(cache).get('version')==VERSION and read(cache).get('sourceSha256')==data['sourceSha256']:
        measure=read(cache)
    else:
        probe=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',source]).stdout)
        pts=[float(f['best_effort_timestamp_time']) for f in probe['frames'] if 'best_effort_timestamp_time' in f]
        raw=subprocess.run(['ffmpeg','-v','error','-i',str(source),'-map','0:v:0','-vf','scale=96:54','-pix_fmt','gray','-fps_mode','passthrough','-f','rawvideo','-'],check=True,capture_output=True).stdout
        frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,54,96)
        if len(frames)!=len(pts):raise ValueError('decoded frames and real timestamp count differ')
        diff=np.abs(np.diff(frames.astype(np.float32),axis=0)).mean(axis=(1,2))/255
        candidates=[]
        ffmpeg_times=data['cuts']['times']
        selected=set()
        for t in ffmpeg_times:
            if pts:selected.add(min(range(len(pts)),key=lambda k:abs(pts[k]-t)))
        for i,d in enumerate(diff,1):
            near=diff[max(0,i-5):min(len(diff),i+4)]
            if d>.06 and d>max(.001,float(np.median(near)))*2.5:selected.add(i)
        for i in sorted(selected):
            if not 0<i<len(pts):continue
            neighbourhood=np.concatenate((diff[max(0,i-5):max(0,i-1)],diff[i:min(len(diff),i+4)]))
            baseline=float(np.median(neighbourhood)) if len(neighbourhood) else 0
            candidates.append({'frameBefore':i-1,'frameAfter':i,'beforeTime':pts[i-1],'afterTime':pts[i],
                'frameIntervalSeconds':pts[i]-pts[i-1],'pixelChange':round(float(diff[i-1]),5),
                'localContrastRatio':round(float(diff[i-1])/max(.001,baseline),2),
                'status':'adjacent_frame_change_candidate','notProof':'运动、闪光、变形也可能触发，尚不等于剪辑硬切。'})
        indices=sorted({i for c in candidates for i in [c['frameBefore'],c['frameAfter']]})
        frames_dir=folder/'frames';frames_dir.mkdir(exist_ok=True)
        if indices:
            extract_selected_frames(source,indices,frames_dir)
        names={idx:f'precision/frames/frame-{j+1:05d}.jpg' for j,idx in enumerate(indices)}
        for c in candidates:c.update(beforeImage=names[c['frameBefore']],afterImage=names[c['frameAfter']])
        has_audio=any(s['codec_type']=='audio' for s in read(out/'probe.json')['streams'])
        onsets=[]
        if has_audio:
            pcm=subprocess.run(['ffmpeg','-v','error','-i',str(source),'-vn','-ac','2','-ar','24000','-f','f32le','-'],capture_output=True,check=True).stdout
            onsets,_=transient_times(np.frombuffer(pcm,dtype='<f4').reshape(-1,2),24000)
        measure={'version':VERSION,'sourceSha256':data['sourceSha256'],'frameCount':len(pts),'cuts':candidates,
                 'soundTransients':onsets,'audioResolutionSeconds':.01,'audioWindowSeconds':.04,
                 'audioStatus':'mixed_audio_energy_not_sfx_classification'}
        save(cache,measure)
    sfx=[];sync=[]
    for w in data['windows']:
        for i,e in enumerate(w.get('analysis',{}).get('sfx',[])):
            target=w['start']+e['start'];actual=nearest(measure['soundTransients'],target,.15)
            sfx.append({'id':f'sfx-{w["start"]}-{i}','modelStart':target,'modelEnd':w['start']+e['end'],
                'description':e.get('description'),'measuredNearbyTransient':actual,
                'deltaMs':round((actual-target)*1000,2) if actual is not None else None,
                'status':'nearby_mixed_transient' if actual is not None else 'no_nearby_transient',
                'precisionClaim':'不改写模型时间；瞬态不证明音效存在，也不排除缓慢起音音效。'})
        for e in w.get('analysis',{}).get('sync',[]):
            a=w['start']+e['audioTime'];v=w['start']+e['visualTime']
            sound=nearest(measure['soundTransients'],a,.15)
            frame=nearest([c['afterTime'] for c in measure['cuts']],v,.15)
            sync.append({'modelVisualTime':v,'modelAudioTime':a,'description':e.get('description'),
                'measuredVisualChange':frame,'measuredSoundTransient':sound,
                'measuredDeltaMs':round((sound-frame)*1000,2) if frame is not None and sound is not None else None,
                'status':'temporal_proximity_only' if frame is not None and sound is not None else 'insufficient_local_evidence',
                'modelQualityWarning':e.get('qualityWarning')})
    result={**measure,'sfxChecks':sfx,'syncChecks':sync,'reviewStatus':'machine_evidence_not_semantically_verified'}
    save(out/'precision.json',result)
    return result
