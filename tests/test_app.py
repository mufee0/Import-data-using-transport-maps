import io
from openpyxl import Workbook
from fastapi.testclient import TestClient
from app.main import app
from app.db import DB_PATH

client=TestClient(app)

def setup_module():
    if DB_PATH.exists(): DB_PATH.unlink()
    from app.db import init_db; init_db()

def xlsx(rows):
    wb=Workbook(); ws=wb.active; ws.append(['Employee ID','Name','Email','Department','Location'])
    for r in rows: ws.append(r)
    out=io.BytesIO(); wb.save(out); return out.getvalue()

def test_health(): assert client.get('/health').status_code==200

def test_import_and_transform():
    content=xlsx([['SB-1001','Ravi Kumar','ravi@test.com','ServiceNow','Hyderabad'],['SB-1002','Sanjay Gopa','sanjay@test.com','ServiceNow','Hyderabad']])
    r=client.post('/api/import/upload',files={'file':('sample.xlsx',content,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')})
    assert r.status_code==200
    iid=r.json()['import_set_id']
    t=client.post(f'/api/import-sets/{iid}/transform',json={'transform_map_id':1})
    assert t.status_code==200 and t.json()['inserted']==2

def test_coalesce_update_and_ignore():
    content=xlsx([['SB-1001','Ravi Updated','new@test.com','Salesforce','Chennai'],['SB-1003','New Person','new3@test.com','ServiceNow','Bengaluru']])
    r=client.post('/api/import/upload',files={'file':('update.xlsx',content,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')})
    iid=r.json()['import_set_id']; t=client.post(f'/api/import-sets/{iid}/transform',json={'transform_map_id':1}).json()
    assert t['updated']==1 and t['inserted']==1
    same=xlsx([['SB-1001','Ravi Updated','new@test.com','Salesforce','Chennai']])
    r=client.post('/api/import/upload',files={'file':('same.xlsx',same,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')})
    iid=r.json()['import_set_id']; t=client.post(f'/api/import-sets/{iid}/transform',json={'transform_map_id':1}).json()
    assert t['ignored']==1

def test_reports_and_ai():
    assert client.get('/api/reports/department').status_code==200
    assert client.get('/api/reports/location').status_code==200
    assert client.get('/api/transform-history').status_code==200
    r=client.post('/api/ai/analyze',json={'question':'Explain the latest import'})
    assert r.status_code==200 and 'answer' in r.json()
