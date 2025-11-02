# FastAPI Application

## Overview
This is a FastAPI application designed for testing implementation. 


## Installation
To get started with this FastAPI application, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/smandalsid/ExpenseMgr-fastapi-mssql-server-docker-alembic.git
    cd ExpenseMgr-fastapi-postgres-docker-alembic
    ```
2. **Request for the env variables**:

3. **Run the dockerized application**:
   ```bash
   make build
   ```

4. **Test the dockerized application**:
    ```bash
    make test
    ```

## Usage
To run the application without docker, use the following steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/smandalsid/ExpenseMgr-fastapi-mssql-server-docker-alembic.git
    cd ExpenseMgr-fastapi-postgres-docker-alembic
    ```
2. **Request for the env variables**:
   
3. **Create virtual environment**:
   ```bash
   python3 -m venv .venv
   ```

4. **Activate the environment**:
   ```bash
   source .venv/bin/activate
   ```

5. **Install dependencies (Poetry is prerequisite)**:
   ```bash
   poetry install
   ```

6. **Create a database docker container**:
   ```bash
   docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=Password123' -p 1433:1433 --name expensemgr-msssql -d mcr.microsoft.com/mssql/server:2022-latest
   ```

5. **Start the application**:
   ```bash
   poetry run fastapi run expensemgr/main.py
   ```

5. **Test the application**:
   ```bash
   pytest --cov=expensemgr --cov-report=html -vv
   ```
