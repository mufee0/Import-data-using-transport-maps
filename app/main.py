from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .config import settings
from .db import init_db
from .importer import rows_from_bytes
from .services import create_import_set, get_import_set, list_import_sets, transform, employees, report_department, report_location, report_history, stats
from .schemas import TransformRequest, AIRequest
from .ai import answer

@asynccontextmanager
async def lifespan(_app):
    init_db()
    yield

app=FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
init_db()
origins=[x.strip() for x in settings.cors_origins.split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins if origins != ["*"] else ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=Path(__file__).parent/"static"), name="static")


@app.get("/", include_in_schema=False)
def home(): return FileResponse(Path(__file__).parent/"templates"/"index.html")

@app.get("/health")
def health(): return {"status":"ok","service":settings.app_name}

@app.post("/api/import/upload")
async def upload(file: UploadFile=File(...)):
    if not file.filename.lower().endswith((".xlsx",".csv")):
        raise HTTPException(400,"Upload an .xlsx or .csv file")
    try:
        content=await file.read()
        rows=rows_from_bytes(file.filename,content)
        iid=create_import_set(file.filename,rows)
        return {"message":"Import Set created","import_set_id":iid,"row_count":len(rows)}
    except ValueError as e: raise HTTPException(400,str(e))

@app.get("/api/import-sets")
def imports(): return list_import_sets()

@app.get("/api/import-sets/{iid}")
def import_detail(iid:int):
    data=get_import_set(iid)
    if not data: raise HTTPException(404,"Import Set not found")
    return data

@app.post("/api/import-sets/{iid}/transform")
def run_transform(iid:int, req:TransformRequest=TransformRequest()):
    try: return transform(iid,req.transform_map_id)
    except ValueError as e: raise HTTPException(400,str(e))

@app.get("/api/employees")
def employee_list(): return employees()

@app.get("/api/reports/department")
def dept(): return report_department()

@app.get("/api/reports/location")
def loc(): return report_location()

@app.get("/api/reports/list")
def list_report(): return employees()

@app.get("/api/transform-history")
def history(): return report_history()

@app.get("/api/dashboard")
def dashboard(): return {"stats":stats(),"department":report_department(),"location":report_location(),"history":report_history()}

@app.post("/api/ai/analyze")
async def ai(req:AIRequest): return await answer(req.question,req.import_set_id)
