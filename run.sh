#!/bin/sh

sqlite3 data/databases/testDB.db <<EOF
DELETE FROM simulations;
DELETE FROM stats;
EOF
python src/metrics/main.py

# chmod +x ./run.sh