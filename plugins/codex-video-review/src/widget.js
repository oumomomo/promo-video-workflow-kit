import {App} from '@modelcontextprotocol/ext-apps';

const app=new App({name:'codex-video-review',version:'0.1.0'},{availableDisplayModes:['inline','fullscreen']},{autoResize:true});
const $=id=>document.getElementById(id),video=$('video'),canvas=$('marks'),ctx=canvas.getContext('2d');
const browserMode=Boolean(window.__VIDEO_REVIEW_BOOTSTRAP__);
let payload=null,notes=[],draft=[],draftImages=[],drawing=null,tool='box',busy=false,sending=false,selectedId=null;
let browserBridge=null;
let localSendAvailable=false;
let sendSupported=!browserMode;
let sentNoteIds=new Set();
let sendWatch=null;
let backgrounded=false,recoveringVideo=false;
const fmt=n=>{n=Math.max(0,Number(n)||0);return `${String(Math.floor(n/60)).padStart(2,'0')}:${String(Math.floor(n%60)).padStart(2,'0')}.${Math.floor(n*10)%10}`;};
let statusTimer=null;
const status=s=>{clearTimeout(statusTimer);$('status').textContent=s;if(s&&!/失败|错误|无法|未发出|未完成/.test(s))statusTimer=setTimeout(()=>{$('status').textContent='';},4500);};
function setExpanded(expanded){
  document.body.classList.toggle('review-expanded',expanded);
  $('expand').textContent=expanded?'缩小画面':'放大打标';
  $('expand').setAttribute('aria-pressed',String(expanded));
  $('expand').setAttribute('aria-label',expanded?'退出放大打标画面':'放大打标画面');
  resize();
}
$('expand').onclick=()=>setExpanded(!document.body.classList.contains('review-expanded'));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.body.classList.contains('review-expanded'))setExpanded(false);});
function resultData(result){return result?._meta?.widgetData||result?.structuredContent||result?.result?.structuredContent||null;}
function setPayload(result){
  const data=resultData(result);if(!data?.video?.url)return;
  payload=data;notes=data.notes||[];video.src=data.video.url;
  renderNotes();
}
if(!browserMode){
  app.addEventListener('toolresult',setPayload);
  app.connect().then(()=>{const host=app.getHostContext?.();if(host?.toolResult)setPayload(host.toolResult);app.requestDisplayMode?.({mode:'fullscreen'}).catch(()=>{});}).catch(e=>status('Codex 组件连接失败：'+e.message));
  window.addEventListener('message',e=>{if(e.data?.method==='ui/notifications/tool-result')setPayload(e.data?.params?.result||e.data?.params);});
}
else{
  browserBridge=Promise.race([
    app.connect().then(()=>true).catch(()=>false),
    new Promise(resolve=>setTimeout(()=>resolve(false),1200)),
  ]).then(async connected=>{
    if(payload?.sendCapabilityUrl){
      try{const response=await fetch(payload.sendCapabilityUrl);const capability=await response.json();localSendAvailable=response.ok&&capability.available===true;}catch{}
    }
    sendSupported=connected||Boolean(window.openai?.sendFollowUpMessage)||localSendAvailable;
    updateSendLabel();
    return connected;
  });
}
function resize(){const rect=canvas.getBoundingClientRect(),dpr=devicePixelRatio||1;canvas.width=Math.round(rect.width*dpr);canvas.height=Math.round(rect.height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);draw();}
new ResizeObserver(resize).observe(canvas);
function drawMark(mark,color='#fb514e'){
  const w=canvas.clientWidth,h=canvas.clientHeight,pts=mark.points.map(([x,y])=>[x*w,y*h]);
  if(pts.length<2)return;ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=3;ctx.lineCap='round';ctx.lineJoin='round';ctx.beginPath();
  if(mark.type==='box'){const a=pts[0],b=pts.at(-1);ctx.rect(a[0],a[1],b[0]-a[0],b[1]-a[1]);}
  else{ctx.moveTo(...pts[0]);for(const p of (mark.type==='pen'?pts.slice(1):[pts.at(-1)]))ctx.lineTo(...p);}
  ctx.stroke();
  if(mark.type==='arrow'){const a=pts[0],b=pts.at(-1),v=Math.atan2(b[1]-a[1],b[0]-a[0]);ctx.beginPath();ctx.moveTo(...b);ctx.lineTo(b[0]-14*Math.cos(v-.5),b[1]-14*Math.sin(v-.5));ctx.moveTo(...b);ctx.lineTo(b[0]-14*Math.cos(v+.5),b[1]-14*Math.sin(v+.5));ctx.stroke();}
}
function draw(){ctx.clearRect(0,0,canvas.clientWidth,canvas.clientHeight);if(!video.paused)return;for(const [index,note] of notes.entries())if(Math.abs(note.time-video.currentTime)<.17)for(const mark of note.marks){drawMark(mark,note.id===selectedId?'#ff8a00':'#fba93d');if(mark.type==='box'){const [x,y]=mark.points[0],px=x*canvas.clientWidth,py=y*canvas.clientHeight;ctx.fillStyle='#1d2430';ctx.fillRect(px,py-22,25,22);ctx.fillStyle='#fff';ctx.font='bold 13px sans-serif';ctx.fillText(String(index+1),px+7,py-6);}}for(const mark of draft)drawMark(mark);if(drawing)drawMark(drawing);}
function point(e){const r=canvas.getBoundingClientRect();return [Math.max(0,Math.min(1,(e.clientX-r.left)/r.width)),Math.max(0,Math.min(1,(e.clientY-r.top)/r.height))];}
canvas.addEventListener('pointerdown',e=>{if(!payload)return;video.pause();canvas.setPointerCapture(e.pointerId);drawing={type:tool,points:[point(e),point(e)]};draw();});
canvas.addEventListener('pointermove',e=>{if(!drawing)return;const p=point(e);if(tool==='pen'){if(drawing.points.length<300)drawing.points.push(p);}else drawing.points[1]=p;draw();});
function finish(){if(!drawing)return;if(drawing.points.length>=2)draft.push(drawing);drawing=null;draw();}
canvas.addEventListener('pointerup',finish);canvas.addEventListener('pointercancel',finish);
document.querySelectorAll('[data-tool]').forEach(b=>b.addEventListener('click',()=>{tool=b.dataset.tool;document.querySelectorAll('[data-tool]').forEach(x=>x.classList.toggle('active',x===b));}));
$('undo').onclick=()=>{draft.pop();draw();};$('clear').onclick=()=>{draft=[];draw();};
$('play').onclick=()=>{if(video.paused)video.play();else video.pause();};
video.addEventListener('play',()=>{$('play').textContent='暂停';draw();});video.addEventListener('pause',()=>{$('play').textContent='播放';draw();});
video.addEventListener('loadedmetadata',()=>{const ratio=video.videoWidth/video.videoHeight;$('stage').style.aspectRatio=String(ratio);$('stage').style.setProperty('--video-ratio',String(ratio));$('duration').textContent=fmt(video.duration);resize();});
video.addEventListener('timeupdate',()=>{$('time').textContent=fmt(video.currentTime);$('seek').value=video.duration?Math.round(video.currentTime/video.duration*1000):0;draw();});
// Chromium can discard a background tab's decoded video surface while leaving
// the media element in its playing state. Rebuild that surface when the tab
// returns, keeping the frame and playback state the reviewer was using.
async function recoverVideo(){
  if(!payload||recoveringVideo||document.hidden)return;
  recoveringVideo=true;
  const time=Number.isFinite(video.currentTime)?video.currentTime:0;
  const resume=!video.paused&&!video.ended;
  try{
    video.pause();
    video.load();
    await new Promise((resolve,reject)=>{
      if(video.readyState>=1){resolve();return;}
      video.addEventListener('loadedmetadata',resolve,{once:true});
      video.addEventListener('error',()=>reject(new Error('视频重新加载失败')),{once:true});
    });
    if(time>0&&Number.isFinite(video.duration)){
      video.currentTime=Math.min(time,Math.max(0,video.duration-0.001));
      await new Promise(resolve=>video.addEventListener('seeked',resolve,{once:true}));
    }
    if(resume)await video.play();
    else draw();
  }catch(error){status(`视频画面恢复失败：${error.message}。请重试播放。`);}
  finally{recoveringVideo=false;}
}
function resumeVisibleVideo(){if(document.hidden||!backgrounded)return;backgrounded=false;recoverVideo();}
document.addEventListener('visibilitychange',()=>{if(document.hidden)backgrounded=true;else resumeVisibleVideo();});
window.addEventListener('blur',()=>{backgrounded=true;});
window.addEventListener('focus',resumeVisibleVideo);
window.addEventListener('pageshow',event=>{if(event.persisted)recoverVideo();});
$('seek').oninput=()=>{if(video.duration)video.currentTime=Number($('seek').value)/1000*video.duration;};
$('back').onclick=()=>{video.pause();video.currentTime=Math.max(0,video.currentTime-1/30);};
$('forward').onclick=()=>{video.pause();video.currentTime=Math.min(video.duration,video.currentTime+1/30);};
function updateSendLabel(){
  const pending=notes.filter(note=>!sentNoteIds.has(note.id));
  const count=document.createElement('span');count.className='send-count';count.textContent=String(pending.length);
  $('ask').replaceChildren(document.createTextNode('发送 '),count,document.createTextNode(' 条待发送标注'));
  $('ask').disabled=sending||!pending.length||!sendSupported;
  $('ask').title=sendSupported?'发送到打开此打标页的 Codex 任务':'当前浏览器页无法向 Codex 任务发送；标注仍可保存';
}
function reviewPrompt(pending){
  const lines=pending.map((note,index)=>{
    const regions=note.marks.map(mark=>{const xs=mark.points.map(p=>p[0]),ys=mark.points.map(p=>p[1]);return `${mark.type} 横向 ${Math.round(Math.min(...xs)*100)}–${Math.round(Math.max(...xs)*100)}%、纵向 ${Math.round(Math.min(...ys)*100)}–${Math.round(Math.max(...ys)*100)}%`;});
    const images=(note.images||[]).map(image=>`${payload.projectDir}/${image.relativePath}`);
    return `${index+1}. 标注 #${notes.indexOf(note)+1}，${note.time.toFixed(3)} 秒：${note.text}\n   此条对应的画面标记：${regions.join('；')||'无'}${images.length?`\n   此条参考图：${images.join('；')}`:''}`;
  });
  return `请按以下 ${pending.length} 条视频标注修改当前候选片。每条文字仅对应它自己的画面区域和参考图，同一时间点的其他标注是独立建议。参考图属于用户反馈，不自动视为产品 UI 原片。\n视频：${payload.video.path}\nSHA-256：${payload.video.sha256}\n${lines.join('\n')}\n精确画线坐标可用 codex-video-review 的 get_video_review_notes 读取，仅在需要时调用。只改标注涉及的片段，保留未标注镜头、总时长与音轨，交付时逐条核对。`;
}
function renderDraftImages(){
  const list=$('draft-images');list.replaceChildren();
  for(const [index,image] of draftImages.entries()){
    const item=document.createElement('div');item.className='image-item';
    const preview=document.createElement('img');preview.src=image.dataUrl;preview.alt=image.name;
    const name=document.createElement('span');name.textContent=image.name;
    const remove=document.createElement('button');remove.type='button';remove.textContent='×';remove.setAttribute('aria-label',`移除参考图 ${image.name}`);
    remove.onclick=()=>{draftImages.splice(index,1);renderDraftImages();};
    item.append(preview,name,remove);list.append(item);
  }
}
async function addImages(files){
  const images=[...files].filter(file=>file.type.startsWith('image/'));
  if(draftImages.length+images.length>5)throw new Error('每条标注最多添加 5 张参考图');
  for(const file of images){
    if(!['image/png','image/jpeg','image/webp','image/gif'].includes(file.type))throw new Error('只支持 PNG、JPEG、WebP 或 GIF 图片');
    if(file.size>8_000_000)throw new Error('每张参考图最多 8 MB');
    const dataUrl=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=()=>reject(new Error('图片读取失败'));reader.readAsDataURL(file);});
    draftImages.push({name:file.name||`参考图-${draftImages.length+1}`,mimeType:file.type,dataUrl});
  }
  renderDraftImages();
  if(images.length)status(`已添加 ${images.length} 张参考图；保存标注后才会写入项目。`);
}
$('comment').addEventListener('paste',event=>{
  const images=[...(event.clipboardData?.items||[])].filter(item=>item.kind==='file'&&item.type.startsWith('image/')).map(item=>item.getAsFile()).filter(Boolean);
  if(!images.length)return;
  event.preventDefault();addImages(images).catch(error=>status(error.message));
});
$('add-images').onclick=()=>$('image-input').click();
$('image-input').addEventListener('change',event=>{addImages(event.target.files).catch(error=>status(error.message));event.target.value='';});
async function changeSavedNote(change){
  if(!payload)throw new Error('视频还没有加载');
  if(browserMode){const response=await fetch(payload.noteUrl,{method:'POST',headers:{'Content-Type':'application/json','Origin':location.origin},body:JSON.stringify(change)});const saved=await response.json();if(!response.ok)throw new Error(saved.error||'修改失败');return saved;}
  const name=change.action==='delete'?'delete_video_review_note':'update_video_review_note';
  const result=await app.callServerTool({name,arguments:{projectDir:payload.projectDir,filePath:payload.video.path,sha256:payload.video.sha256,id:change.id,...(change.action==='update'?{text:change.text}:{})}});
  if(result.isError)throw new Error(result.content?.find(x=>x.type==='text')?.text||'修改失败');
  return result.structuredContent;
}
function selectNote(note){selectedId=note.id;video.pause();video.currentTime=note.time;renderNotes();draw();}
function editNote(note){
  selectNote(note);
  const card=[...$('notes').children,...$('sent-notes').children].find(x=>x.dataset.noteId===note.id);
  const text=card?.querySelector('.note-text');if(!text)return;
  const editor=document.createElement('textarea');editor.className='note-editor';editor.value=note.text;editor.setAttribute('aria-label','修改标注内容');text.replaceWith(editor);editor.focus();editor.select();
  editor.addEventListener('click',e=>e.stopPropagation());
  let finished=false;
  const commit=async(cancel=false)=>{
    if(finished)return;finished=true;
    const value=editor.value.trim();if(cancel||value===note.text){renderNotes();return;}
    if(!value){status('标注内容不能为空');renderNotes();return;}
    try{const saved=await changeSavedNote({action:'update',id:note.id,text:value});notes=saved.notes;sentNoteIds.delete(note.id);renderNotes();refreshSendStatus();status('标注已更新，这一版需要重新发送。');}
    catch(error){renderNotes();status(`标注修改失败：${error.message}`);}
  };
  editor.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();commit(true);}else if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();commit();}});
  editor.addEventListener('blur',()=>commit());
}
function renderNotes(){
  const list=$('notes'),sentList=$('sent-notes');list.replaceChildren();sentList.replaceChildren();
  $('pending-count').textContent=String(notes.filter(note=>!sentNoteIds.has(note.id)).length);
  $('sent-count').textContent=String(notes.filter(note=>sentNoteIds.has(note.id)).length);
  $('sent-section').hidden=sentNoteIds.size===0;updateSendLabel();
  for(const [index,note] of notes.entries()){
    const card=document.createElement('div');card.className='note'+(note.id===selectedId?' selected':'');card.dataset.noteId=note.id;
    const header=document.createElement('div');header.className='note-header';const time=document.createElement('time');time.textContent=`#${index+1} · ${fmt(note.time)}`;header.append(time);
    if(note.id===selectedId){const remove=document.createElement('button');remove.className='note-delete';remove.type='button';remove.title='删除这条标注';remove.setAttribute('aria-label',`删除 ${fmt(note.time)} 的标注`);remove.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M10 4h4M6 7l1 13h10l1-13M10 11v6m4-6v6"/></svg>';remove.onclick=async e=>{e.stopPropagation();if(busy)return;busy=true;remove.disabled=true;try{const saved=await changeSavedNote({action:'delete',id:note.id});notes=saved.notes;sentNoteIds.delete(note.id);selectedId=null;renderNotes();draw();refreshSendStatus();status('这条标注已删除。');}catch(error){status(`删除失败：${error.message}`);remove.disabled=false;}finally{busy=false;}};header.append(remove);}
    const content=document.createElement('div');content.className='note-text';content.textContent=note.text;content.title='点击修改标注内容';content.onclick=e=>{e.stopPropagation();editNote(note);};
    card.append(header,content);
    if(note.images?.length){
      const gallery=document.createElement('div');gallery.className='note-images';
      for(const image of note.images){
        const link=document.createElement('a');link.className='image-item';link.href=payload.imageBaseUrl+image.sha256;link.target='_blank';link.rel='noopener';link.title=`查看参考图 ${image.name}`;
        const preview=document.createElement('img');preview.src=link.href;preview.alt=image.name;
        const name=document.createElement('span');name.textContent=image.name;
        link.append(preview,name);link.onclick=e=>e.stopPropagation();gallery.append(link);
      }
      card.append(gallery);
    }
    card.onclick=e=>{if(!e.target.closest('.note-editor'))selectNote(note);};(sentNoteIds.has(note.id)?sentList:list).append(card);
  }
}
async function save(){
  if(!payload)throw new Error('视频还没有加载');const text=$('comment').value.trim();if(!text)throw new Error('先填写这处怎么改');
  if(!draft.length&&!draftImages.length)throw new Error('先在画面上标记，或添加参考图');
  if(busy)return;busy=true;$('save').disabled=true;
  try{const note={id:crypto.randomUUID(),time:Math.round(video.currentTime*1000)/1000,text,marks:structuredClone(draft),images:structuredClone(draftImages)};
    let saved;
    if(browserMode){const response=await fetch(payload.saveUrl,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(note)});saved=await response.json();if(!response.ok)throw new Error(saved.error||'保存失败');}
    else{const result=await app.callServerTool({name:'save_video_review_note',arguments:{projectDir:payload.projectDir,filePath:payload.video.path,sha256:payload.video.sha256,note}});if(result.isError)throw new Error(result.content?.find(x=>x.type==='text')?.text||'保存失败');saved=result.structuredContent;}
    notes=saved?.notes||[...notes,note];draft=[];draftImages=[];renderDraftImages();$('comment').value='';selectedId=note.id;renderNotes();draw();refreshSendStatus();status(`已保存 ${fmt(note.time)} 的标注。`);return note;
  }finally{busy=false;$('save').disabled=false;}
}
$('save').onclick=()=>save().catch(e=>status(e.message));
function showSendState(result,announce=false){
  if(Array.isArray(result.sentNoteIds)){sentNoteIds=new Set(result.sentNoteIds);renderNotes();draw();}
  if(result.state==='failed')status(`发送失败：${result.error||'原因未知'}。可以重试。`);
  else if(announce&&result.state==='submitting')status('正在发送…');
  else if(announce&&['queued','submitted','processing','completed'].includes(result.state))status('已提交。');
}
async function refreshSendStatus(){
  if(!browserMode||!payload?.sendStatusUrl)return;
  try{const response=await fetch(payload.sendStatusUrl);if(response.ok){const result=await response.json();sentNoteIds=new Set(result.sentNoteIds||[]);renderNotes();draw();return result;}}catch{}
}
async function watchSendStatus(){
  if(sendWatch||!payload?.sendStatusUrl)return;
  sendWatch=setInterval(async()=>{
    try{const response=await fetch(payload.sendStatusUrl);if(!response.ok)throw new Error('无法读取任务状态');
      const result=await response.json();showSendState(result);
      if(result.state==='completed'||result.state==='failed'){clearInterval(sendWatch);sendWatch=null;}
    }catch{clearInterval(sendWatch);sendWatch=null;status('无法确认目标任务是否继续处理，请在 Codex 任务中查看。');}
  },3000);
}
$('ask').onclick=async()=>{if(sending)return;sending=true;$('ask').disabled=true;try{
  if($('comment').value.trim()||draft.length||draftImages.length)throw new Error('还有未保存的标注或参考图，请先点“保存这处标注”');if(!payload||!notes.length)throw new Error('请先保存标注');
  const pending=notes.filter(note=>!sentNoteIds.has(note.id));if(!pending.length)throw new Error('没有待发送标注');
  const prompt=reviewPrompt(pending);
  status(`正在发送 ${pending.length} 条待发送标注…`);
  if(browserMode){
    if(localSendAvailable){const response=await fetch(payload.sendUrl,{method:'POST'});const result=await response.json();if(!response.ok)throw new Error(result.error||'发送失败');showSendState(result,true);if(['submitting','queued','submitted','processing'].includes(result.state))watchSendStatus();}
    else if(window.openai?.sendFollowUpMessage){await window.openai.sendFollowUpMessage({prompt});sentNoteIds=new Set([...sentNoteIds,...pending.map(note=>note.id)]);renderNotes();status('已发出会话消息，等待 Codex 任务处理。');}
    else if(await browserBridge){const result=await app.sendMessage({role:'user',content:[{type:'text',text:prompt}]});if(result.isError)throw new Error('Codex 拒绝了会话消息');sentNoteIds=new Set([...sentNoteIds,...pending.map(note=>note.id)]);renderNotes();status('已发出会话消息，等待 Codex 任务处理。');}
    else throw new Error('当前页面没有可用的 Codex 会话发送接口');
  }
  else{const result=await app.sendMessage({role:'user',content:[{type:'text',text:prompt}]});if(result.isError)throw new Error('Codex 拒绝了会话消息');sentNoteIds=new Set([...sentNoteIds,...pending.map(note=>note.id)]);renderNotes();status('已发出会话消息，等待 Codex 任务处理。');}
}catch(e){status(`修改请求未发出：${e.message}`);}finally{sending=false;updateSendLabel();}};
if(browserMode){
  setPayload({structuredContent:window.__VIDEO_REVIEW_BOOTSTRAP__});
  if(payload?.sendStatusUrl)fetch(payload.sendStatusUrl).then(r=>r.json()).then(result=>{
    showSendState(result);if(['submitting','queued','submitted','processing'].includes(result.state))watchSendStatus();
  }).catch(()=>{});
}
