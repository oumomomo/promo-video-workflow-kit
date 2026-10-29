"""Read already imported workflow evidence from the sole workbench database."""
import json
import asset_exclusion


def read(db):
    rows = db.execute('''SELECT i.*,v.content_hash,v.payload_json
        FROM library_items i JOIN library_item_versions v ON v.version_id=i.current_version_id
        ORDER BY i.item_id''').fetchall()
    excluded = asset_exclusion.workflow_ids(db)
    items = []
    for r in rows:
        if r['item_id'] in excluded:
            continue
        payload = json.loads(r['payload_json'])
        kind = r['entity_kind']
        role = ('fact' if kind == 'fact' else 'motion_candidate' if kind == 'motion_capability'
                else 'visual_inspiration' if r['language_scope'] == 'language_independent'
                else 'inspiration' if kind == 'method' else 'reference')
        items.append(dict(sourceId=r['item_id'], itemId=r['item_id'], sourceSystem=r['source_system'],
            sourcePath=r['source_path'], sourceUrl=r['source_url'], sourceHash=r['content_hash'],
            entityKind=kind, title=r['title'], sourceLanguage=r['source_language'],
            analysisLanguage=r['analysis_language'], languageScope=r['language_scope'],
            reviewStatus=r['review_status'], capabilityStatus=r['capability_status'],
            rightsStatus=r['rights_status'], aiEligible=r['ai_status']=='eligible',
            aiEnabled=r['ai_status']=='eligible', tags=json.loads(r['tags_json']),
            compactPayload=payload, usageRole=role, storedVersion=r['current_version_id'], catalogStored=True))
    return {'items': items, 'count': len(items), 'source': 'unified_workbench_database'}
