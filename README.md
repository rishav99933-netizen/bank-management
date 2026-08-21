# Bank Management System — Flask

Deployment-ready Flask + MySQL/MariaDB version.

## Local run

1. Create the `bank_management` database.
2. Run `schema.sql` in MySQL/MariaDB.
3. Set these environment variables if your credentials differ:
   - `MYSQLHOST`
   - `MYSQLPORT`
   - `MYSQLUSER`
   - `MYSQLPASSWORD`
   - `MYSQLDATABASE`
   - `SECRET_KEY`
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python -m flask --app app run`

## Railway deployment

Use a Railway MySQL service and a Railway web service. Railway provides the MySQL variables `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, and `MYSQLDATABASE`; add the same variables to the Flask service or reference the database service variables. Build command:

`pip install -r requirements.txt`

Start command:

`gunicorn app:app`

Before first use, execute `schema.sql` in the Railway MySQL console.
