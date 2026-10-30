#!/usr/bin/env python3
"""Portable project manifest, FFmpeg compositor and evidence checks. No model calls.

Only project-local JSON and media are written. This is not an asset-library backend.
All subprocesses use argv, never shell expressions from a plan.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VERSION = '0.7.3-local-candidate'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def local(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError('项目文件必须使用相对路径')
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise ValueError('文件不能越出项目目录：' + name)
    return path


def run(argv):
    result = subprocess.run(list(map(str, argv)), capture_output=True, text=True)
    if result.returncode:
        raise ValueError('执行失败：' + Path(str(argv[0])).name + '\n' + result.stderr[-5000:])
    return result


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path]).stdout)


def number(value, low, high, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(label + ' 数值无效')
    return value


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', value):
        raise ValueError('ID只允许字母、数字、下划线和短横线')
    return value


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('缺少：' + label)
    return value


def project(args):
    root = Path(args.project).expanduser().resolve()
    if not (root / 'workflow/brief.json').is_file():
        raise ValueError('先对新项目运行 init')
    return root


def init(args):
    root = Path(args.project).expanduser().resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError('init 要求空目录，拒绝覆盖已有项目')
    for name in ('workflow', 'assets', 'out', 'checks'):
        (root / name).mkdir(parents=True, exist_ok=True)
    brief = {'schemaVersion': 1, 'request': args.brief, 'createdAt': now(),
             'status': 'working_brief_not_user_approval', 'constraints': [],
             'sourceMode': 'new_topic', 'fictional': None}
    write(root / 'workflow/brief.json', brief)
    write(root / 'workflow/assets.json', {'schemaVersion': 1, 'assets': []})
    plan = {'schemaVersion': 1, 'briefSha256': sha(root / 'workflow/brief.json'),
            'scriptSha256': None, 'canvas': {'width': 1920, 'height': 1080, 'fps': 30},
            'visualDirection': '', 'paletteBasis': '', 'shots': [],
            'audio': {'mode': 'silent', 'reason': '', 'tracks': []}}
    write(root / 'workflow/plan.json', plan)
    return {'state': 'initialized', 'project': str(root), 'next': 'Agent写稿、确定画面方向；用lock-script锁定实际稿件，再填写plan.json。',
            'videoCreated': False, 'mainLibraryWritten': False}


def lock_script(args):
    root = project(args)
    source = Path(args.file).expanduser().resolve()
    data = source.read_bytes()
    if not data.strip():
        raise ValueError('脚本不能为空')
    data.decode('utf-8')
    dest = root / 'workflow/script.locked.txt'
    if dest.exists():
        if dest.read_bytes() != data:
            raise ValueError('已有锁定脚本不同；请保留原项目并显式建立改稿版本')
    else:
        dest.write_bytes(data)
    plan = read(root / 'workflow/plan.json')
    plan['scriptSha256'] = sha(dest)
    plan['briefSha256'] = sha(root / 'workflow/brief.json')
    write(root / 'workflow/plan.json', plan)
    write(root / 'workflow/script-record.json', {'sha256': sha(dest), 'origin': args.origin,
          'lockedAt': now(), 'meaning': 'file_integrity_only_not_user_approval'})
    return {'state': 'script_locked', 'sha256': sha(dest), 'userApproved': False}


def add_asset(args):
    root = project(args)
    identifier(args.id)
    source = Path(args.file).expanduser().resolve()
    if not source.is_file():
        raise ValueError('素材文件不存在')
    digest = sha(source)
    ledger = read(root / 'workflow/assets.json')
    if any(a['id'] == args.id for a in ledger['assets']):
        raise ValueError('素材ID已存在；修改素材请使用新ID以保留历史')
    ext = source.suffix.lower()
    if not re.fullmatch(r'\.[a-z0-9]{1,8}', ext):
        raise ValueError('素材扩展名无效')
    dest = root / 'assets' / (args.id + '-' + digest[:12] + ext)
    if not dest.exists():
        shutil.copyfile(source, dest)
    if sha(dest) != digest:
        raise ValueError('素材副本哈希不一致')
    item = {'id': args.id, 'path': str(dest.relative_to(root)), 'sha256': digest, 'kind': args.kind,
            'origin': {'type': args.origin, 'detail': args.source},
            'rights': {'status': args.rights, 'basis': args.basis}, 'addedAt': now()}
    ledger['assets'].append(item)
    write(root / 'workflow/assets.json', ledger)
    return {'state': 'project_asset_copied', 'asset': item, 'mainLibraryWritten': False}


def load_plan(root):
    plan = read(root / 'workflow/plan.json')
    if plan.get('schemaVersion') != 1:
        raise ValueError('不支持的分镜格式')
    if sha(root / 'workflow/brief.json') != plan.get('briefSha256'):
        raise ValueError('需求已变更，请重新核对分镜并更新briefSha256')
    if sha(root / 'workflow/script.locked.txt') != plan.get('scriptSha256'):
        raise ValueError('锁定脚本已变更，拒绝沿用旧分镜')
    nonempty(plan.get('visualDirection'), '视觉方向')
    nonempty(plan.get('paletteBasis'), '色彩依据')
    canvas = plan['canvas']
    width = number(canvas['width'], 64, 3840, '宽度')
    height = number(canvas['height'], 64, 3840, '高度')
    fps = number(canvas['fps'], 1, 60, '帧率')
    if any(int(n) != n for n in (width, height, fps)) or width % 2 or height % 2:
        raise ValueError('画幅须为偶数整数，帧率须为整数')
    assets = {}
    for a in read(root / 'workflow/assets.json')['assets']:
        aid = identifier(a['id'])
        if aid in assets:
            raise ValueError('重复素材ID')
        path = local(root, a['path'])
        if not path.is_file() or sha(path) != a['sha256']:
            raise ValueError('素材缺失或内容变更：' + aid)
        if a['rights']['status'] not in ('owned', 'licensed', 'generated', 'internal_only'):
            raise ValueError('素材权限声明未完成：' + aid)
        nonempty(a['rights']['basis'], '素材权限依据')
        nonempty(a['origin']['detail'], '素材来源')
        if a['kind'] not in ('image', 'video', 'audio', 'font', 'other'):
            raise ValueError('未知素材类型')
        assets[aid] = a

    def asset(aid, kinds):
        if aid not in assets or assets[aid]['kind'] not in kinds:
            raise ValueError('引用素材不存在或类型不符：' + str(aid))
        return local(root, assets[aid]['path'])

    shots = plan['shots']
    if not isinstance(shots, list) or not shots or len(shots) > 200:
        raise ValueError('分镜应有1至200个镜头')
    script = (root / 'workflow/script.locked.txt').read_text(encoding='utf-8')
    script_ranges = []
    ids = set()
    for s in shots:
        sid = identifier(s['id'])
        if sid in ids:
            raise ValueError('重复镜头ID')
        ids.add(sid)
        duration = number(s['duration'], 1 / fps, 300, '镜头时长')
        if abs(duration * fps - round(duration * fps)) > 1e-5:
            raise ValueError('镜头时长必须对齐整数帧')
        for key in ('event', 'focus', 'acceptance', 'connection'):
            nonempty(s.get(key), sid + '.' + key)
        start, end = s['scriptRange']
        if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= len(script):
            raise ValueError('脚本字符区间无效：' + sid)
        script_ranges.append((start, end))
        p = asset(s['asset'], ('image', 'video'))
        if assets[s['asset']]['kind'] == 'video':
            begin = number(s.get('in', 0), 0, 86400, '视频入点')
            if begin + duration > float(probe(p)['format']['duration']) + 1 / fps:
                raise ValueError('视频区间越界：' + sid)
            if 'zoom' in s or 'pan' in s:
                raise ValueError('视频镜头不接受静图zoom/pan；复杂运动请先制作成视频素材')
        else:
            zoom = s.get('zoom', [1, 1])
            if len(zoom) != 2:
                raise ValueError('zoom应有起止两个数值')
            for z in zoom:
                number(z, 1, 4, '静图缩放')
            pan = s.get('pan', [[0.5, 0.5], [0.5, 0.5]])
            if len(pan) != 2 or any(len(pair) != 2 for pair in pan):
                raise ValueError('pan应为两个[x,y]位置')
            for pair in pan:
                for n in pair:
                    number(n, 0, 1, '静图构图位置')
        for layer in s.get('layers', []):
            asset(layer['asset'], ('image',))
            lo = number(layer.get('start', 0), 0, duration, '叠层起点')
            hi = number(layer.get('end', duration), 0, duration, '叠层终点')
            if lo >= hi:
                raise ValueError('叠层时间区间无效')
            for key in ('fadeIn', 'fadeOut'):
                number(layer.get(key, 0), 0, (hi - lo) / 2, '叠层淡入淡出')
    covered = set()
    for lo, hi in script_ranges:
        covered.update(range(lo, hi))
    if any(i not in covered and not c.isspace() for i, c in enumerate(script)):
        raise ValueError('分镜遗漏锁定脚本中的非空白内容')
    total = sum(s['duration'] for s in shots)
    if total > 1800:
        raise ValueError('此短片执行器限制总时长30分钟')
    audio = plan['audio']
    nonempty(audio.get('reason'), '声音方案')
    if audio.get('mode') not in ('silent', 'mix'):
        raise ValueError('声音模式应为silent或mix')
    if (audio['mode'] == 'silent') != (len(audio['tracks']) == 0):
        raise ValueError('静音模式须无音轨，混音模式至少一条音轨')
    for t in audio['tracks']:
        p = asset(t['asset'], ('audio', 'video'))
        nonempty(t.get('role'), '声音职责')
        at = number(t.get('at', 0), 0, total, '声音落点')
        begin = number(t.get('in', 0), 0, 86400, '声音入点')
        length = number(t['duration'], 0.001, total, '声音时长')
        if at + length > total + 1 / fps or begin + length > float(probe(p)['format']['duration']) + 0.02:
            raise ValueError('声音区间越界')
        if not any(st['codec_type'] == 'audio' for st in probe(p)['streams']):
            raise ValueError('声音素材没有音轨')
        number(t.get('gainDb', 0), -60, 12, '声音增益')
        for key in ('fadeIn', 'fadeOut'):
            number(t.get(key, 0), 0, length / 2, '声音淡入淡出')
    return plan, assets, total


def validate(args):
    root = project(args)
    p, assets, total = load_plan(root)
    return {'state': 'plan_validated', 'shots': len(p['shots']), 'seconds': total,
            'assets': len(assets), 'scriptCovered': True, 'rightsMeaning': 'recorded_declarations_not_legal_verification',
            'aesthetic': 'pending_human_review', 'userApproved': False}


def render(args):
    root = project(args)
    p, assets, total = load_plan(root)
    input_hashes = {name: sha(root / name) for name in ('workflow/plan.json', 'workflow/assets.json')}
    output = local(root, args.out)
    if output.suffix.lower() != '.mp4' or output.exists():
        raise ValueError('输出须为新的.mp4文件，拒绝覆盖')
    output.parent.mkdir(parents=True, exist_ok=True)
    width, height, fps = (int(p['canvas'][key]) for key in ('width', 'height', 'fps'))
    commands = []
    with tempfile.TemporaryDirectory(prefix='.render-', dir=root / 'out') as td:
        tmp = Path(td)
        clips = []
        for index, shot in enumerate(p['shots']):
            duration = shot['duration']
            frames = round(duration * fps)
            source = local(root, assets[shot['asset']]['path'])
            cmd = ['ffmpeg', '-v', 'error', '-nostdin', '-threads', '2']
            is_image = assets[shot['asset']]['kind'] == 'image'
            if is_image:
                cmd += ['-loop', '1', '-framerate', str(fps), '-i', str(source)]
                z0, z1 = shot.get('zoom', [1, 1])
                start, end = shot.get('pan', [[0.5, 0.5], [0.5, 0.5]])
                phase = f'min(on/{max(frames - 1, 1)},1)'
                z = f'{z0}+({z1}-{z0})*{phase}'
                x = f'(iw-iw/zoom)*({start[0]}+({end[0]}-{start[0]})*{phase})'
                y = f'(ih-ih/zoom)*({start[1]}+({end[1]}-{start[1]})*{phase})'
                base = f"scale={width*2}:{height*2}:force_original_aspect_ratio=increase,crop={width*2}:{height*2},zoompan=z='{z}':x='{x}':y='{y}':d=1:s={width}x{height}:fps={fps}"
            else:
                cmd += ['-ss', str(shot.get('in', 0)), '-i', str(source)]
                base = f'scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps={fps}'
            filters = [f'[0:v]{base},setsar=1,setpts=N/({fps}*TB),format=rgba[base]']
            last = 'base'
            for li, layer in enumerate(shot.get('layers', []), 1):
                cmd += ['-loop', '1', '-framerate', str(fps), '-i', str(local(root, assets[layer['asset']]['path']))]
                lo, hi = layer.get('start', 0), layer.get('end', duration)
                f = f'[{li}:v]scale={width}:{height},format=rgba'
                if layer.get('fadeIn', 0):
                    f += f",fade=t=in:st={lo}:d={layer['fadeIn']}:alpha=1"
                if layer.get('fadeOut', 0):
                    f += f",fade=t=out:st={hi-layer['fadeOut']}:d={layer['fadeOut']}:alpha=1"
                f += f'[layer{li}]'
                filters += [f, f"[{last}][layer{li}]overlay=0:0:shortest=1:enable='gte(t,{lo})*lt(t,{hi})'[composite{li}]"]
                last = f'composite{li}'
            filters += [f'[{last}]format=yuv420p[v]']
            clip = tmp / f'{index:03d}.mp4'
            cmd += ['-filter_complex_threads', '1', '-filter_complex', ';'.join(filters), '-map', '[v]',
                    '-an', '-frames:v', str(frames), '-r', str(fps), '-c:v', 'libx264', '-preset', 'medium',
                    '-crf', str(args.crf), '-threads', '2', '-video_track_timescale', str(fps * 512), str(clip)]
            run(cmd); commands.append(cmd); clips.append(clip)
        # Generated numeric filenames only; no external paths enter the concat grammar.
        concat = tmp / 'concat.txt'
        concat.write_text(''.join(f"file '{c.name}'\n" for c in clips), encoding='utf-8')
        joined = tmp / 'joined.mp4'
        cmd = ['ffmpeg', '-v', 'error', '-nostdin', '-f', 'concat', '-safe', '1', '-i', str(concat), '-c', 'copy', str(joined)]
        run(cmd); commands.append(cmd)
        # Build final inside temp: failed muxes do not leave a misleading candidate.
        finished = tmp / 'finished.mp4'
        cmd = ['ffmpeg', '-v', 'error', '-nostdin', '-i', str(joined)]
        tracks = p['audio']['tracks']
        if tracks:
            filters = []
            for i, track in enumerate(tracks, 1):
                cmd += ['-i', str(local(root, assets[track['asset']]['path']))]
                length, begin = track['duration'], track.get('in', 0)
                f = f'[{i}:a]atrim=start={begin}:duration={length},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={track.get("gainDb",0)}dB'
                if track.get('fadeIn', 0):
                    f += f',afade=t=in:st=0:d={track["fadeIn"]}'
                if track.get('fadeOut', 0):
                    f += f',afade=t=out:st={length-track["fadeOut"]}:d={track["fadeOut"]}'
                f += f',adelay={round(track.get("at",0)*1000)}:all=1[a{i}]'
                filters.append(f)
            filters.append(''.join(f'[a{i}]' for i in range(1, len(tracks)+1)) +
                           f'amix=inputs={len(tracks)}:normalize=0,apad=whole_dur={total},atrim=duration={total}[audio]')
            cmd += ['-filter_complex', ';'.join(filters), '-map', '0:v:0', '-map', '[audio]',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000']
        else:
            cmd += ['-map', '0:v:0', '-an', '-c:v', 'copy']
        cmd += ['-t', str(total), '-movflags', '+faststart', str(finished)]
        run(cmd); commands.append(cmd)
        # Re-check the inputs before publishing, including changes during a long render.
        load_plan(root)
        if any(sha(root / name) != digest for name, digest in input_hashes.items()):
            raise ValueError('渲染期间分镜或素材清单变更，拒绝交付混合版本')
        shutil.copyfile(finished, output)
    receipt = {'state': 'rendered_candidate', 'version': VERSION, 'file': str(output.relative_to(root)),
               'sha256': sha(output), 'planSha256': sha(root / 'workflow/plan.json'),
               'scriptSha256': p['scriptSha256'], 'seconds': total, 'createdAt': now(),
               'commands': commands, 'userApproved': False, 'aesthetic': 'pending_human_review',
               'normalSpeedPlayback': 'not_recorded', 'audioListening': 'not_recorded'}
    write(output.with_suffix('.render.json'), receipt)
    return {key: value for key, value in receipt.items() if key != 'commands'}


def check(args):
    root = project(args)
    p, assets, total = load_plan(root)
    video = local(root, args.file)
    receipt = read(video.with_suffix('.render.json'))
    if sha(video) != receipt['sha256'] or sha(root / 'workflow/plan.json') != receipt['planSha256']:
        raise ValueError('视频或分镜与渲染回执不一致')
    metadata = probe(video)
    stream = next(s for s in metadata['streams'] if s['codec_type'] == 'video')
    expected = p['canvas']
    errors = []
    duration = float(metadata['format']['duration'])
    if abs(duration - total) > 1 / expected['fps'] + 0.025:
        errors.append('时长不符')
    if any(stream[key] != expected[key] for key in ('width', 'height')):
        errors.append('画幅不符')
    rate = stream['avg_frame_rate'].split('/')
    if abs(int(rate[0]) / int(rate[1]) - expected['fps']) > 0.001:
        errors.append('帧率不符')
    expected_frames = sum(round(s['duration'] * expected['fps']) for s in p['shots'])
    counted = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
                             '-show_entries', 'stream=nb_read_frames', '-of', 'json', video]).stdout)
    frames = int(counted['streams'][0]['nb_read_frames'])
    if frames != expected_frames:
        errors.append('帧数不符')
    decoded = run(['ffmpeg', '-v', 'error', '-xerror', '-nostdin', '-i', video, '-f', 'null', '-'])
    has_audio = any(s['codec_type'] == 'audio' for s in metadata['streams'])
    if has_audio != (p['audio']['mode'] == 'mix'):
        errors.append('音轨存在性与计划不符')
    audio = {'present': has_audio, 'listening': 'not_performed_by_signal_check'}
    if has_audio:
        volume = run(['ffmpeg', '-v', 'info', '-nostdin', '-i', video, '-vn', '-af', 'volumedetect', '-f', 'null', '-']).stderr
        match = re.search(r'max_volume:\s*(-?[\d.]+) dB', volume)
        audio['peakDbfs'] = float(match.group(1)) if match else None
        audio['nearFullScaleWarning'] = audio['peakDbfs'] is not None and audio['peakDbfs'] >= -0.1
        write(root / 'checks' / (video.stem + '-audio-signal.json'), {'log': volume, **audio})
    folder = root / 'checks' / (video.stem + '-frames')
    folder.mkdir(parents=True, exist_ok=True)
    samples = []
    t = 0
    for shot in p['shots']:
        for offset, label in ((0, 'start'), (shot['duration'] / 2, 'mid'), (shot['duration'] - 1/expected['fps'], 'end')):
            seconds = round(t + offset, 6)
            dest = folder / f'{shot["id"]}-{label}.jpg'
            run(['ffmpeg', '-v', 'error', '-nostdin', '-ss', seconds, '-i', video, '-frames:v', '1',
                 '-vf', 'scale=960:-2', '-y', dest])
            if not dest.is_file():
                errors.append('抽帧失败')
            else:
                samples.append({'time': seconds, 'path': str(dest.relative_to(root)), 'sha256': sha(dest)})
        t += shot['duration']
    report = {'state': 'technical_pass' if not errors else 'technical_fail', 'errors': errors,
              'video': str(video.relative_to(root)), 'sha256': sha(video), 'planSha256': receipt['planSha256'],
              'duration': duration, 'decodedFrames': frames, 'fullDecode': 'pass', 'canvas': expected,
              'audio': audio, 'samples': samples, 'createdAt': now(), 'userApproved': False,
              'visualSampleInspection': 'pending_actual_viewing', 'fullNormalSpeedPlayback': 'pending',
              'aesthetic': 'pending_human_review', 'rights': 'declarations_only'}
    dest = root / 'checks' / (video.stem + '-technical.json')
    write(dest, report)
    if errors:
        raise ValueError('技术检查失败：' + ', '.join(errors))
    return {'state': report['state'], 'report': str(dest), 'sha256': report['sha256'],
            'decodedFrames': frames, 'audio': audio, 'humanReview': 'pending'}


def doctor(args):
    result = {'version': VERSION, 'python': sys.version.split()[0], 'tools': {},
              'modelProvider': 'host_agent_required', 'imageOrVideoGeneration': 'external_tool_or_user_media',
              'cloudCalls': 0}
    for tool in ('ffmpeg', 'ffprobe'):
        binary = shutil.which(tool)
        result['tools'][tool] = {'available': bool(binary), 'path': binary}
        if binary:
            result['tools'][tool]['version'] = run([binary, '-version']).stdout.splitlines()[0]
    result['ready'] = sys.version_info >= (3, 10) and all(t['available'] for t in result['tools'].values())
    if result['tools']['ffmpeg']['available']:
        result['h264EncoderAvailable'] = 'libx264' in run(['ffmpeg', '-hide_banner', '-encoders']).stdout
        result['ready'] = result['ready'] and result['h264EncoderAvailable']
    return result


def main():
    parser = argparse.ArgumentParser(description='新题目视频制作：项目初始化、素材拷贝、分镜验证、渲染与技术检查。创意由宿主Agent执行。')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    p = sub.add_parser('init'); p.add_argument('--project', required=True); p.add_argument('--brief', required=True)
    p = sub.add_parser('lock-script'); p.add_argument('--project', required=True); p.add_argument('--file', required=True)
    p.add_argument('--origin', choices=['user_provided', 'agent_authored_for_requested_task'], required=True)
    p = sub.add_parser('add-asset'); p.add_argument('--project', required=True); p.add_argument('--id', required=True)
    p.add_argument('--file', required=True); p.add_argument('--kind', choices=['image', 'video', 'audio', 'font', 'other'], required=True)
    p.add_argument('--origin', choices=['user_provided', 'generated', 'public_download', 'project_authored'], required=True)
    p.add_argument('--source', required=True); p.add_argument('--rights', choices=['owned', 'licensed', 'generated', 'internal_only'], required=True)
    p.add_argument('--basis', required=True)
    for name in ('validate', 'render', 'check'):
        p = sub.add_parser(name); p.add_argument('--project', required=True)
        if name == 'render':
            p.add_argument('--out', required=True); p.add_argument('--crf', type=int, choices=range(12, 31), default=18)
        if name == 'check':
            p.add_argument('--file', required=True)
    args = parser.parse_args()
    try:
        fn = {'init': init, 'lock-script': lock_script, 'add-asset': add_asset, 'validate': validate,
              'render': render, 'check': check, 'doctor': doctor}[args.command]
        print(json.dumps(fn(args), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, FileNotFoundError, TypeError, StopIteration) as exc:
        print(json.dumps({'state': 'error', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
