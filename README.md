# Employee Management System
Local learning project. Extract into a NEW folder to avoid overwriting your existing work. In PowerShell from the extracted folder:

    python -m venv venv
    .\venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python manage.py makemigrations employees
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Open http://127.0.0.1:8000/ and log in with your superuser. Create departments and designations before employees. For employee login, create a regular user (not staff) in /admin/ under Users, set a password, and link that user to an employee record using the employee edit form. Staff users are treated as HR. Only trusted HR should receive staff status. Deactivation blocks access to employee records but does not disable the linked login itself.

Leave uses calendar days and deducts balance on approval. Salary is a record, not payroll calculation. No bank details are stored. Reports export employee directory CSV only. Bootstrap uses an internet CDN. No sample personal data included. Use fake records only. DEBUG and the fallback secret are for local development; production needs separate security configuration and permission review. Do not expose this server publicly. Migrations are generated on first setup. Runtime tests were not executed in the creation environment.
