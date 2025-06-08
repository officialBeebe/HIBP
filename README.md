# Glossary

## Flask/ Core

- [Flask](https://flask.palletsprojects.com/en/stable/)
- [Jinja](https://jinja.palletsprojects.com/en/stable/)
- [SQLAlchemy](https://www.postgresql.org/docs/)

## Postgres

- [Postgres](https://www.postgresql.org/docs/)
- [pgnotify](https://github.com/djrobstep/pgnotify)
- [pg_notify in Postgres trigger function](https://stackoverflow.com/questions/5412474/using-pg-notify-in-postgresql-trigger-function)

## Packaging/ Migration

- [Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [Writing your `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [SetupTools](https://setuptools.pypa.io/en/latest/)
- [Version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers)
- [Download dependencies declared in pyproject.toml](https://stackoverflow.com/questions/62408719/download-dependencies-declared-in-pyproject-toml-using-pip)

# Getting Started

### Setup Postgres

You should first initialize a Postgres database and enable a user with USAGE and CREATE privileges. Connect to Postgres
as a superuser and enter the following commands to create the database, user, and configure permissions:

``` SQL 
CREATE DATABASE "hibp-service";

CREATE ROLE "hibp-service-user" WITH PASSWORD "strong-secure-password";

GRANT CONNECT ON DATABASE "hibp-service" TO  "hibp-service-user";
```

### Clone project and install dependencies

``` bash
git clone https://github.com/officialBeebe/HIBP.git
cd HIBP

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install this project as an editable package (required for Alembic, Flask CLI, etc)
pip install -e .
```

### Set environment variables

This project uses a config.py to expose a Config class that exports a db_url() method. This method builds a
SQLAlchemy-compatible URL using values from a `.env` file or the current shell environment. You can inject the variables
manually like so:

```bash
export DB_DRIVER=postgresql+psycopg2 \
       DB_USER=hibp-service-user \
       DB_PASSWORD=strong-secure-password \
       DB_HOST=127.0.0.1 \
       DB_PORT=5432 \
       DB_DATABASE=hibp-service
```

Alternatively, create a `.env` file in the root of the project with the same values and load them using `python-dotenv`
or `./config.py`.

### Apply database migrations

This project uses Alembic manage schema migrations. Peep inside `./alembic/versions` for revision history.

Apply these migrations using the following command:

``` bash
alembic upgrade head
```

### Run application

```bash
flask run
```

You should be able to access the app at `http://127.0.0.1:5000/` by default. 