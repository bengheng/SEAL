#!/bin/bash

mv cloakdb cloakdb.old
mv logdb logdb.old
sqlite3 cloakdb < schema.sql
sqlite3 logdb < log_schema.sql
sudo chown john:www-data cloakdb
sudo chmod g+w cloakdb
