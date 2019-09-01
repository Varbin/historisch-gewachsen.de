#!/bin/bash

cd "${0%/*}"

git pull

[[ -d venv ]] || python3 -m virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements.txt -U
python db_build.py

exec gunicorn app:app
