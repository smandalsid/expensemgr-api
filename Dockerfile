FROM python:3.12

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"


# Download the package to configure the Microsoft repo
RUN curl -sSL -O https://packages.microsoft.com/config/ubuntu/24.10/packages-microsoft-prod.deb
# Install the package
RUN dpkg -i packages-microsoft-prod.deb
# Delete the file
RUN rm packages-microsoft-prod.deb

# Install the driver
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18
# optional: for bcp and sqlcmd
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools18
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
RUN source ~/.bashrc
# optional: for unixODBC development headers
RUN apt-get install -y unixodbc-dev

RUN pip install pyodbc
    
WORKDIR /expensemgr

RUN apt-get update && apt-get install -y \
   curl \
&& rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:${PATH}"

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

RUN chmod a+x expensemgr/docker/application/entrypoint.sh
RUN chmod a+x expensemgr/docker/wait-for-db.sh
RUN chmod a+x expensemgr/docker/application/create-db.sh
RUN chmod a+x expensemgr/docker/application/setup.sql

EXPOSE 8000

CMD "expensemgr/docker/application/entrypoint.sh"
