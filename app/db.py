import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "import_transform_maps.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

SCHEMA = """
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL UNIQUE,
    employee_name TEXT NOT NULL,
    email TEXT NOT NULL,
    department TEXT NOT NULL,
    location TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS import_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    source_filename TEXT NOT NULL,
    row_count INTEGER NOT NULL,
    state TEXT NOT NULL DEFAULT 'Ready',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS import_rows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_set_id INTEGER NOT NULL,
    row_number INTEGER NOT NULL,
    employee_id TEXT,
    employee_name TEXT,
    email TEXT,
    department TEXT,
    location TEXT,
    status TEXT NOT NULL DEFAULT 'Ready',
    message TEXT,
    FOREIGN KEY(import_set_id) REFERENCES import_sets(id)
);
CREATE TABLE IF NOT EXISTS transform_maps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    source_table TEXT NOT NULL,
    target_table TEXT NOT NULL,
    coalesce_field TEXT NOT NULL DEFAULT 'employee_id',
    active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS field_maps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transform_map_id INTEGER NOT NULL,
    source_field TEXT NOT NULL,
    target_field TEXT NOT NULL,
    coalesce INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(transform_map_id) REFERENCES transform_maps(id)
);
CREATE TABLE IF NOT EXISTS transform_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_set_id INTEGER NOT NULL,
    transform_map_id INTEGER NOT NULL,
    state TEXT NOT NULL,
    total INTEGER NOT NULL,
    inserted INTEGER NOT NULL,
    updated INTEGER NOT NULL,
    ignored INTEGER NOT NULL,
    errors INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(import_set_id) REFERENCES import_sets(id),
    FOREIGN KEY(transform_map_id) REFERENCES transform_maps(id)
);
"""

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as db:
        db.executescript(SCHEMA)
        row = db.execute("SELECT COUNT(*) c FROM transform_maps").fetchone()
        if row["c"] == 0:
            cur = db.execute("INSERT INTO transform_maps(name, source_table, target_table, coalesce_field) VALUES(?,?,?,?)",
                             ("Sample Spreadsheet Import", "u_employee_import", "u_employee_test", "employee_id"))
            tm_id = cur.lastrowid
            mappings = [
                ("employee_id", "employee_id", 1),
                ("employee_name", "employee_name", 0),
                ("email", "email", 0),
                ("department", "department", 0),
                ("location", "location", 0),
            ]
            db.executemany("INSERT INTO field_maps(transform_map_id,source_field,target_field,coalesce) VALUES(?,?,?,?)",
                            [(tm_id,*m) for m in mappings])
