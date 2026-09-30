import csv, io
from openpyxl import load_workbook

REQUIRED = ["employee_id", "employee_name", "email", "department", "location"]
ALIASES = {
    "employee id":"employee_id", "employee_id":"employee_id", "employeeid":"employee_id",
    "name":"employee_name", "employee name":"employee_name", "employee_name":"employee_name",
    "email":"email", "department":"department", "location":"location"
}

def normalize_header(v):
    return str(v or "").strip().lower().replace("-", " ").replace("_", " ")

def rows_from_bytes(filename: str, content: bytes):
    if filename.lower().endswith(".csv"):
        text = content.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
    else:
        wb = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
    if not rows:
        raise ValueError("The spreadsheet is empty.")
    headers = [ALIASES.get(normalize_header(x), normalize_header(x).replace(" ", "_")) for x in rows[0]]
    missing = [h for h in REQUIRED if h not in headers]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    result = []
    for values in rows[1:]:
        if not any(str(v or "").strip() for v in values):
            continue
        item = {h: (str(values[i]).strip() if i < len(values) and values[i] is not None else "") for i,h in enumerate(headers) if h}
        result.append({k:item.get(k,"") for k in REQUIRED})
    return result
