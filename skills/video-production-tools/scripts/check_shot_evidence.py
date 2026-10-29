#!/usr/bin/env python3
"""Check the mechanical part of a product UI shot-to-source evidence gate.

This cannot decide whether a recording actually shows the claimed UI or action.
"""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def checked_file(root, value, expected_sha256, label, errors):
    if not value or not isinstance(value, str):
        errors.append(f'{label}: file path is missing')
        return
    path = (root / value).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        errors.append(f'{label}: file is missing or outside workspace: {value}')
    elif not expected_sha256 or digest(path) != expected_sha256:
        errors.append(f'{label}: SHA-256 is missing or does not match')


def check(manifest_path, workspace_root, require_ready, recreation_stage=None):
    data = json.loads(manifest_path.read_text())
    errors = []
    if data.get('schemaVersion') != 1:
        errors.append('unsupported schemaVersion')
    storyboard = workspace_root / (data.get('lockedStoryboard') or data.get('storyboardBasis') or '')
    if not storyboard.resolve().is_relative_to(workspace_root) or not storyboard.is_file():
        errors.append('storyboard basis is missing')
    sources = {}
    for source in data.get('sources', []):
        asset_id = source.get('assetId')
        path = workspace_root / source.get('path', '')
        if not asset_id or asset_id in sources:
            errors.append(f'duplicate or missing source asset ID: {asset_id}')
            continue
        sources[asset_id] = source
        if not path.resolve().is_relative_to(workspace_root) or not path.is_file():
            errors.append(f'{asset_id}: source file is missing')
        elif digest(path) != source.get('sha256') or asset_id != 'asset:' + source.get('sha256', ''):
            errors.append(f'{asset_id}: file SHA-256 or asset ID mismatch')
    shot_ids = set()
    pending = []
    for shot in data.get('shots', []):
        shot_id = shot.get('shotId')
        if not shot_id or shot_id in shot_ids:
            errors.append(f'duplicate or missing shot ID: {shot_id}')
            continue
        shot_ids.add(shot_id)
        for field in ('intent', 'sourceEvidence', 'inherit', 'mayAdapt', 'forbid', 'gaps', 'status'):
            if field not in shot:
                errors.append(f'{shot_id}: missing {field}')
        if shot.get('status') not in {'ready', 'pending_evidence'}:
            errors.append(f'{shot_id}: unsupported status')
        for evidence in shot.get('sourceEvidence', []):
            asset_id = evidence.get('assetId')
            if asset_id not in sources:
                errors.append(f'{shot_id}: unknown source {asset_id}')
            if not evidence.get('observed'):
                errors.append(f'{shot_id}: source observation is empty')
            if not evidence.get('keyframesSeconds') and not evidence.get('imageRegion'):
                errors.append(f'{shot_id}: missing keyframe time or image region')
        if recreation_stage:
            evidence_ids = {item.get('assetId') for item in shot.get('sourceEvidence', [])}
            recreation = shot.get('sourceRecreation')
            if evidence_ids:
                if not isinstance(recreation, dict):
                    errors.append(f'{shot_id}: sourceRecreation is required for source-backed UI')
                else:
                    asset_id = recreation.get('assetId')
                    if asset_id not in evidence_ids:
                        errors.append(f'{shot_id}: sourceRecreation assetId must match sourceEvidence')
                    if not recreation.get('sourceMomentSeconds') and recreation.get('sourceMomentSeconds') != 0 \
                            and not recreation.get('sourceImageRegion'):
                        errors.append(f'{shot_id}: sourceRecreation needs a source moment or image region')
                    checked_file(workspace_root, recreation.get('sourceFramePath'),
                                 recreation.get('sourceFrameSha256'),
                                 f'{shot_id} source frame', errors)
                    if not isinstance(recreation.get('recreate'), list) or not recreation['recreate'] \
                            or not all(isinstance(item, str) and item.strip() for item in recreation['recreate']):
                        errors.append(f'{shot_id}: sourceRecreation needs concrete structure to recreate')
                    if not isinstance(recreation.get('adaptContent'), list) \
                            or not all(isinstance(item, str) and item.strip() for item in recreation['adaptContent']):
                        errors.append(f'{shot_id}: sourceRecreation needs an adaptContent list')
                    if recreation_stage == 'delivery':
                        checked_file(workspace_root, recreation.get('candidateFramePath'),
                                     recreation.get('candidateFrameSha256'),
                                     f'{shot_id} candidate frame', errors)
                        if recreation.get('comparisonStatus') != 'pass' or not recreation.get('comparisonNotes') \
                                or not recreation.get('reviewedBy'):
                            errors.append(f'{shot_id}: delivery needs a reviewed source/candidate comparison')
            elif shot.get('renderMode') != 'concept_demo' or not shot.get('conceptReason') \
                    or not shot.get('conceptAuthorization'):
                errors.append(f'{shot_id}: no source evidence; concept_demo needs a reason and authorization')
        if shot.get('status') == 'ready':
            for field in ('intent', 'inherit', 'mayAdapt', 'forbid'):
                if not shot.get(field):
                    errors.append(f'{shot_id}: ready requires nonempty {field}')
            if not shot.get('sourceEvidence') or shot.get('gaps') or not shot.get('verifiedBy'):
                errors.append(f'{shot_id}: ready requires evidence, no gaps, and a named verifier')
            for evidence in shot.get('sourceEvidence', []):
                source = sources.get(evidence.get('assetId'))
                suffix = Path(source.get('path', '')).suffix.lower() if source else ''
                required_scope = 'still_reviewed' if suffix in {'.png', '.jpg', '.jpeg', '.webp'} else 'continuous_reviewed'
                if evidence.get('reviewScope') != required_scope:
                    errors.append(f'{shot_id}: ready evidence needs {required_scope}')
                if required_scope == 'continuous_reviewed' and not evidence.get('reviewedTimeRangeSeconds'):
                    errors.append(f'{shot_id}: ready video evidence needs a reviewed time range')
        else:
            pending.append(shot_id)
    if not shot_ids:
        errors.append('manifest has no shots')
    if require_ready and pending:
        errors.append('not ready: ' + ', '.join(pending))
    return {'project': data.get('project'), 'shots': len(shot_ids), 'sources': len(sources),
            'ready': len(shot_ids) - len(pending), 'pending': pending, 'errors': errors}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--workspace-root', type=Path, required=True)
    parser.add_argument('--require-ready', action='store_true')
    parser.add_argument('--recreation-stage', choices=('preproduction', 'delivery'))
    args = parser.parse_args()
    result = check(args.manifest.resolve(), args.workspace_root.resolve(),
                   args.require_ready, args.recreation_stage)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result['errors'] else 0)
