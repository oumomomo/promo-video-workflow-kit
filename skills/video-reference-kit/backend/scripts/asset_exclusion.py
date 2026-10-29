"""One SQL rule shared by the Python gateway and Node workbench."""
from pathlib import Path
SQL = (Path(__file__).resolve().parents[1] / 'src/asset-library/exclusion.sql').read_text()


def blocked(db, rid):
    return bool(db.execute(SQL + 'SELECT 1 FROM blocked WHERE id=?', (rid,)).fetchone())


def workflow_ids(db):
    return {row[0] for row in db.execute(SQL + 'SELECT id FROM blocked_workflow')}
