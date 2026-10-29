WITH RECURSIVE
flagged(id) AS (
 SELECT id FROM asset_records WHERE coalesce(json_extract(metadata,'$.retrievalExcluded'),0)=1
 UNION SELECT a.alias FROM asset_aliases a JOIN flagged f ON a.record_id=f.id
 UNION SELECT a.record_id FROM asset_aliases a JOIN flagged f ON a.alias=f.id
),
blocked(id) AS (
 SELECT id FROM flagged
 UNION
 SELECT other.record_id FROM asset_links own
 JOIN flagged f ON f.id=own.record_id
 JOIN asset_links other ON other.sha=own.sha
 WHERE own.role='source' AND other.role='source'
 UNION SELECT a.alias FROM asset_aliases a JOIN blocked b ON a.record_id=b.id
 UNION SELECT a.record_id FROM asset_aliases a JOIN blocked b ON a.alias=b.id
),
production_records(id) AS (
 SELECT id FROM asset_records WHERE json_extract(metadata,'$.evidenceRole')='production_context'
 UNION SELECT a.alias FROM asset_aliases a JOIN production_records p ON a.record_id=p.id
 UNION SELECT a.record_id FROM asset_aliases a JOIN production_records p ON a.alias=p.id
),
blocked_workflow(id) AS (
 SELECT legacy_id FROM asset_records WHERE id IN (SELECT id FROM production_records) AND legacy_id IS NOT NULL
 UNION SELECT legacy_id FROM asset_legacy_links WHERE record_id IN (SELECT id FROM production_records)
 UNION SELECT 'unified:'||id FROM production_records
 UNION
 SELECT legacy_id FROM asset_records WHERE id IN (SELECT id FROM blocked) AND legacy_id IS NOT NULL
 UNION SELECT legacy_id FROM asset_legacy_links WHERE record_id IN (SELECT id FROM blocked)
 UNION SELECT 'unified:'||id FROM blocked
 UNION SELECT substr(id,8) FROM blocked WHERE substr(id,1,7)='legacy:'
)
