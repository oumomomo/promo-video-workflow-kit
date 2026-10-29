#!/usr/bin/env python3
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ARCHIVE_REL = Path('production-archive/archive.json')


def now():
    return datetime.now(timezone.utc).isoformat()


def archive_path(root):
    return Path(root).resolve() / ARCHIVE_REL


def load(root):
    path = archive_path(root)
    if not path.is_file():
        raise SystemExit(f'archive missing: {path}')
    return path, json.loads(path.read_text(encoding='utf-8'))


def write(path, data):
    # unified-archive-write:v1
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def cmd_init(args):
    path = archive_path(args.project_root)
    if path.exists():
        raise SystemExit(f'archive already exists: {path}')
    data = {
        'schemaVersion': 1,
        'video': {'id': args.video_id, 'title': args.title, 'status': 'production', 'createdAt': now()},
        'univer': {'file': None, 'worktreeId': None, 'baseUnitId': None, 'docUnitId': None, 'boardUnitId': None},
        'script': {'approved': None, 'voiceover': None},
        'motion': {'manifest': None, 'registryRevision': None, 'creativePolicy': 'library-as-springboard'},
        'bgm': [], 'shots': [], 'assets': [], 'renders': [],
        'events': [{'at': now(), 'type': 'archive_initialized'}],
    }
    write(path, data)
    print(path)


def file_hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def iter_paths(data):
    def walk(value, key=''):
        if isinstance(value, dict):
            for k, v in value.items():
                yield from walk(v, k)
        elif isinstance(value, list):
            for item in value:
                yield from walk(item, key)
        elif key in {'path', 'relativePath', 'manifest'} and isinstance(value, str):
            yield value
    yield from walk(data)


def iter_objects(data, location='$'):
    if isinstance(data, dict):
        yield location, data
        for key, value in data.items():
            yield from iter_objects(value, f'{location}.{key}')
    elif isinstance(data, list):
        for index, value in enumerate(data):
            yield from iter_objects(value, f'{location}[{index}]')


def validate_hash(root_path, rel, expected, label, errors):
    if not rel or not expected:
        return
    target = (root_path / rel).resolve()
    try:
        target.relative_to(root_path)
    except ValueError:
        return
    if target.is_file():
        actual = file_hash(target)
        if actual != expected:
            errors.append(f'hash mismatch at {label}: {rel}')


def validate_data(root, data):
    errors = []
    if data.get('schemaVersion') != 1:
        errors.append('unsupported schemaVersion')
    video = data.get('video') or {}
    if not video.get('id') or not video.get('title'):
        errors.append('video id/title missing')
    shot_ids = [item.get('id') for item in data.get('shots', [])]
    if None in shot_ids or len(shot_ids) != len(set(shot_ids)):
        errors.append('shot ids missing or duplicated')
    asset_ids = [item.get('id') for item in data.get('assets', [])]
    if None in asset_ids or len(asset_ids) != len(set(asset_ids)):
        errors.append('asset ids missing or duplicated')
    root_path = Path(root).resolve()
    for rel in sorted(set(iter_paths(data))):
        target = (root_path / rel).resolve()
        try:
            target.relative_to(root_path)
        except ValueError:
            errors.append(f'path escapes project root: {rel}')
            continue
        if not target.exists():
            errors.append(f'file missing: {rel}')
    for location, item in iter_objects(data):
        if item.get('status') == 'accepted':
            missing = [key for key in ('approvedBy', 'approvedAt', 'approvedScope', 'evidence') if not item.get(key)]
            if missing:
                errors.append(f'accepted item missing approval evidence at {location}: {", ".join(missing)}')
        validate_hash(root_path, item.get('relativePath') or item.get('path'), item.get('sha256'), location, errors)
        validate_hash(root_path, item.get('manifest'), item.get('manifestSha256'), f'{location}.manifest', errors)
    approved_script = (data.get('script') or {}).get('approved')
    if approved_script:
        missing = [key for key in ('approvedBy', 'approvedAt', 'approvedScope', 'evidence') if not approved_script.get(key)]
        if missing:
            errors.append(f'approved script missing approval evidence: {", ".join(missing)}')
    for index, render in enumerate(data.get('renders', [])):
        if render.get('status') == 'rejected':
            missing = [key for key in ('rejectedBy', 'rejectedAt', 'rejectionReason', 'evidence') if not render.get(key)]
            if missing:
                errors.append(f'rejected render missing rejection evidence at renders[{index}]: {", ".join(missing)}')
    motion = data.get('motion') or {}
    motion_manifest = motion.get('manifest')
    if motion_manifest:
        target = (root_path / motion_manifest).resolve()
        if target.exists():
            try:
                selection = json.loads(target.read_text(encoding='utf-8'))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f'motion manifest unreadable: {exc}')
            else:
                if selection.get('videoId') != video.get('id'):
                    errors.append('motion manifest videoId mismatch')
                motion_shot_ids = [item.get('shotId') for item in selection.get('shots', [])]
                if None in motion_shot_ids or len(motion_shot_ids) != len(set(motion_shot_ids)):
                    errors.append('motion manifest shot IDs missing or duplicated')
                unknown_shots = sorted(set(motion_shot_ids) - set(shot_ids)) if shot_ids else []
                if unknown_shots:
                    errors.append(f'motion manifest references unknown shots: {", ".join(unknown_shots)}')
    return errors


def cmd_validate(args):
    _, data = load(args.project_root)
    errors = validate_data(args.project_root, data)
    if not errors:
        pass  # Portable validation stays project-local; no implicit database write.
    print(json.dumps({'ok': not errors, 'errors': errors}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


def cmd_audit(args):
    path, data = load(args.project_root)
    errors = validate_data(args.project_root, data)
    motion_manifest = (data.get('motion') or {}).get('manifest')
    motion_count = 0
    if motion_manifest:
        motion_path = Path(args.project_root).resolve() / motion_manifest
        if motion_path.exists():
            try:
                motion_count = len(json.loads(motion_path.read_text(encoding='utf-8')).get('shots', []))
            except (OSError, json.JSONDecodeError):
                pass
    summary = {
        'archive': str(path), 'video': data.get('video'),
        'counts': {key: len(data.get(key, [])) for key in ('bgm', 'shots', 'assets', 'renders')},
        'currentScriptApproved': bool((data.get('script') or {}).get('current')),
        'historicalScopedScriptApproval': bool((data.get('script') or {}).get('approved')),
        'motionSelections': motion_count,
        'errors': errors,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--project-root', required=True)
    init.add_argument('--video-id', required=True)
    init.add_argument('--title', required=True)
    init.set_defaults(func=cmd_init)
    for name, func in [('audit', cmd_audit), ('validate', cmd_validate)]:
        command = sub.add_parser(name)
        command.add_argument('--project-root', required=True)
        command.set_defaults(func=func)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
