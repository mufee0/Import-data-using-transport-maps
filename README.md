# Import Data using Transform Maps — Complete Local Project

This application is a runnable local simulator of the supplied ServiceNow micro-project **Import Data using Transform Maps (Spreadsheet)**. The source workflow loads employee spreadsheet data into an Import Set staging area, maps it to the Employee Test target table, transforms it, enables Employee ID coalescing to prevent duplicates, and builds reports/dashboard views.

## What is implemented

- Excel `.xlsx` and CSV upload
- Import Set staging table
- Employee Test target table
- Transform Map named **Sample Spreadsheet Import**
- Field mappings for Employee ID, Employee Name, Email, Department, Location
- Employee ID configured as the coalesce key
- Transform history with Inserted / Updated / Ignored / Error counts
- Department report
- Location report
- Employee list report
- Dashboard-style consolidated view
- Optional Gemini LLM assistant; deterministic import logic remains independent of the LLM
- REST API + Swagger/OpenAPI
- Automated tests

## Source alignment

The supplied documentation specifies `u_employee_test`, `u_employee_import`, the five employee fields, Transform Map name `Sample Spreadsheet Import`, Auto Map/Mapping Assist, transformation, Coalesce, three reports, and the `Employee Analytics Dashboards` dashboard. The local simulator uses equivalent concepts and exposes them through a browser UI/API instead of requiring a live ServiceNow instance.

## Folder structure

```text
Import-Data-Transform-Maps-Project/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── schemas.py
│   ├── importer.py
│   ├── services.py
│   ├── ai.py
│   ├── main.py
│   ├── templates/index.html
│   └── static/app.js
│   └── static/style.css
├── data/
├── sample_data/
│   ├── Sample Spreadsheet.xlsx
│   └── duplicate_test.xlsx
├── servicenow/
│   ├── 01_configuration.md
│   └── 02_transform_map.md
├── tests/test_app.py
├── requirements.txt
├── .env.example
└── README.md
```

## VS Code setup — Windows

Open the project folder in VS Code and open Terminal → New Terminal.

```powershell
py -3 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\\Scripts\\Activate.ps1
```

Create `.env` from `.env.example`. You may leave `GEMINI_API_KEY` empty; the application has a local fallback assistant.

## Run

```powershell
uvicorn app.main:app --reload
```

Open:

- Application: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Test

```powershell
pytest -q
```

The tests validate upload, transformation, Coalesce update behavior, identical-row ignore behavior, reports, history and AI fallback.

## Test the documented workflow

1. Upload `sample_data/Sample Spreadsheet.xlsx`.
2. Select the generated Import Set.
3. Click **Run Transform**.
4. Confirm employee records appear in the Employee List Report.
5. Review Department and Location reports.
6. Review Transform History.
7. Upload `sample_data/duplicate_test.xlsx` and transform it.
8. Employee IDs already present are **updated** when other values change; identical rows are **ignored**; new Employee IDs are **inserted**.
9. Ask the AI Import Assistant to explain the latest transformation.

## Gemini setup (optional)

Add your Gemini API key to `.env`:

```text
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

The LLM is explanatory only. It never decides whether a row is inserted, updated or ignored.

## Real ServiceNow implementation

This repository does not claim to connect to a ServiceNow instance. For a real instance, follow the supplied document's navigation and create the actual custom target table, Import Set table, Transform Map, field maps, Coalesce setting, reports and dashboard. The local application is intended for demonstration, development, testing and viva/project presentation without requiring a ServiceNow account.
