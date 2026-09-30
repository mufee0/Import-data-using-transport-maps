# ServiceNow Configuration Checklist

Based directly on the supplied project documentation.

## Target table

- Navigation: Tables → Create New
- Label: Employee Test
- Name: `u_employee_test`
- Fields:
  - Employee ID — String
  - Employee Name — String
  - Email — String
  - Department — String
  - Location — String

## Import Set table

- Navigation: Application Navigator → Load Data
- Label: Employee Import
- Name: `u_employee_import` (auto-populated)
- Load the spreadsheet and create the Transform Map.

## First transformation

- Transform Map: Sample Spreadsheet Import
- Source: Employee Import
- Target: Employee Test
- Use Auto Map Matching fields / Mapping Assist.
- Transform the import set.

## Coalesce

Open the Transform Map and its Field Maps related list. Set the Employee ID field's Coalesce value to true. This allows repeated imports to update matching Employee IDs instead of inserting duplicate records.

## Reports

1. Employees by Department — Employee Test, Pie Chart, Group By Department, Count.
2. Employees by Location — Employee Test, Bar Chart, Group By Location, Count.
3. Employee List Report — Employee Test, List, columns Employee ID, Employee Name, Email, Department, Location.

## Dashboard

Create dashboard `Employee Analytics Dashboards`, then add all three reports to it. The source document also describes dashboard ACL/admin-override configuration when using the `PA_DASHBOARDS.FORM` backend form.
