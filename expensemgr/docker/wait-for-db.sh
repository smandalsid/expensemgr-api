#!/bin/bash
# Wait for SQL Server to start
echo "Waiting for SQL Server to start..."
for i in {1..50};
do
 /opt/mssql-tools18/bin/sqlcmd -S tcp:$SQL_SERVER,$SQL_PORT -U $SQL_USER -P $SQL_PASSWORD -Q "SELECT 1" -C&> /dev/null
 if [ $? -eq 0 ]; then
   echo "SQL Server is up."
   break
 else
   echo "Not ready yet..."
   sleep 1
 fi
done