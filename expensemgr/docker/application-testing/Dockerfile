FROM python:3.12

WORKDIR /

ENV PYTHONPATH=/

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
# RUN source ~/.bashrc
# optional: for unixODBC development headers
RUN apt-get install -y unixodbc-dev

RUN pip install pyodbc

RUN apt-get update && apt-get install -y \
   curl \
&& rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:${PATH}"

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

RUN chmod a+x expensemgr/docker/application-testing/entrypoint.sh
RUN chmod a+x expensemgr/docker/wait-for-db.sh
RUN chmod a+x expensemgr/docker/application-testing/create-db.sh
RUN chmod a+x expensemgr/docker/application-testing/setup.sql

CMD "./expensemgr/docker/application-testing/entrypoint.sh"