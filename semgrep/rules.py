# ai-generated: 100% - Codex wrote positive and negative examples for the custom rules.
from datetime import datetime


def cases(db, value):
    # ruleid: dynamic-sql-execute
    db.execute(f"SELECT * FROM {value}", ())
    # ok: dynamic-sql-execute
    db.execute("SELECT * FROM tickets WHERE id = ?", (value,))
    # ruleid: parsed-iso-datetime
    datetime.fromisoformat(value)
    # ok: parsed-iso-datetime
    datetime.now()
