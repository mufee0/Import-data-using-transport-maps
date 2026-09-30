from datetime import datetime
from .db import get_db

REQUIRED = ["employee_id", "employee_name", "email", "department", "location"]

def create_import_set(filename, rows):
    with get_db() as db:
        cur = db.execute("INSERT INTO import_sets(name,source_filename,row_count,state) VALUES(?,?,?,?)",
                         (f"Import {datetime.now().strftime('%Y%m%d-%H%M%S')}", filename, len(rows), "Ready"))
        iid = cur.lastrowid
        for n, r in enumerate(rows, 2):
            db.execute("INSERT INTO import_rows(import_set_id,row_number,employee_id,employee_name,email,department,location) VALUES(?,?,?,?,?,?,?)",
                       (iid,n,r["employee_id"],r["employee_name"],r["email"],r["department"],r["location"]))
        return iid

def get_import_set(iid):
    with get_db() as db:
        s = db.execute("SELECT * FROM import_sets WHERE id=?", (iid,)).fetchone()
        if not s: return None
        rows = db.execute("SELECT * FROM import_rows WHERE import_set_id=? ORDER BY row_number", (iid,)).fetchall()
        return {"id":s["id"],"name":s["name"],"source_filename":s["source_filename"],"row_count":s["row_count"],"state":s["state"],"created_at":s["created_at"],"rows":[dict(r) for r in rows]}

def list_import_sets():
    with get_db() as db:
        return [dict(r) for r in db.execute("SELECT * FROM import_sets ORDER BY id DESC").fetchall()]

def transform(iid, tm_id=1):
    with get_db() as db:
        tm = db.execute("SELECT * FROM transform_maps WHERE id=? AND active=1", (tm_id,)).fetchone()
        if not tm: raise ValueError("Active Transform Map not found")
        rows = db.execute("SELECT * FROM import_rows WHERE import_set_id=? ORDER BY row_number", (iid,)).fetchall()
        if not rows: raise ValueError("Import Set contains no rows")
        inserted=updated=ignored=errors=0
        for r in rows:
            vals = [r[k] or "" for k in REQUIRED]
            if not all(vals):
                errors += 1
                db.execute("UPDATE import_rows SET status='Error', message=? WHERE id=?", ("Required field is empty", r["id"]))
                continue
            existing = db.execute("SELECT id,employee_name,email,department,location FROM employees WHERE employee_id=?", (r["employee_id"],)).fetchone()
            if existing:
                changed = any(existing[k] != r[k] for k in ["employee_name","email","department","location"])
                if changed:
                    db.execute("UPDATE employees SET employee_name=?,email=?,department=?,location=?,updated_at=CURRENT_TIMESTAMP WHERE employee_id=?",
                               (r["employee_name"],r["email"],r["department"],r["location"],r["employee_id"]))
                    updated += 1
                    msg = "Updated existing record using Employee ID coalesce."
                    status="Updated"
                else:
                    ignored += 1
                    msg = "Ignored: identical record already exists."
                    status="Ignored"
            else:
                db.execute("INSERT INTO employees(employee_id,employee_name,email,department,location) VALUES(?,?,?,?,?)", vals)
                inserted += 1
                msg="Inserted new employee record."
                status="Inserted"
            db.execute("UPDATE import_rows SET status=?, message=? WHERE id=?", (status,msg,r["id"]))
        total=len(rows)
        db.execute("UPDATE import_sets SET state='Completed' WHERE id=?", (iid,))
        cur=db.execute("INSERT INTO transform_history(import_set_id,transform_map_id,state,total,inserted,updated,ignored,errors) VALUES(?,?,?,?,?,?,?,?)",
                       (iid,tm_id,"Completed",total,inserted,updated,ignored,errors))
        hid=cur.lastrowid
        return {"history_id":hid,"state":"Completed","total":total,"inserted":inserted,"updated":updated,"ignored":ignored,"errors":errors}

def employees():
    with get_db() as db:
        return [dict(r) for r in db.execute("SELECT * FROM employees ORDER BY employee_id").fetchall()]

def report_department():
    with get_db() as db:
        return [dict(r) for r in db.execute("SELECT department AS label, COUNT(*) AS count FROM employees GROUP BY department ORDER BY count DESC, department").fetchall()]

def report_location():
    with get_db() as db:
        return [dict(r) for r in db.execute("SELECT location AS label, COUNT(*) AS count FROM employees GROUP BY location ORDER BY count DESC, location").fetchall()]

def report_history():
    with get_db() as db:
        return [dict(r) for r in db.execute("SELECT * FROM transform_history ORDER BY id DESC").fetchall()]

def stats():
    with get_db() as db:
        emp=db.execute("SELECT COUNT(*) c FROM employees").fetchone()["c"]
        h=db.execute("SELECT COALESCE(SUM(inserted),0) inserted, COALESCE(SUM(updated),0) updated, COALESCE(SUM(ignored),0) ignored, COALESCE(SUM(errors),0) errors FROM transform_history").fetchone()
        return {"total_employees":emp, **dict(h)}
