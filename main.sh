#!/bin/bash

PROJECT_ROOT=$(dirname "$BASH_SOURCE")
TEMP_CRONTAB_FILE="$PROJECT_ROOT/crontab.temp"
PYTHON_GENERATE_SCRIPT="$PROJECT_ROOT/core/generate.py"

crontab -l >"$TEMP_CRONTAB_FILE"
python3 "$PYTHON_GENERATE_SCRIPT"
crontab "$TEMP_CRONTAB_FILE"
rm "$TEMP_CRONTAB_FILE"
crontab -l
