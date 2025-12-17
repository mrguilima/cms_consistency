#!/bin/bash

echo start.sh: version 1.0.2

CC_DATA=/reports
WM_DATA=/reports/unmerged

echo "--- starting ---"
cd /app

echo "--- CC_DATA <$CC_DATA>: ---"
ls -ld $CC_DATA

echo "--- WM_DATA <$WM_DATA>: ---"
ls -ld $WM_DATA

python -V

echo "--- starting server with: " python app/server.py --um-ignore /store/unmerged/logs/ -p 8400 "$@" $CC_DATA $WM_DATA
python app/server.py --um-ignore /store/unmerged/logs/ -p 8400 "$@" $CC_DATA $WM_DATA
