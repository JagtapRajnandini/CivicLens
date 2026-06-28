#!/usr/bin/env bash
set -e

pip install -r requirements.txt
python create_admin_auto.py
python seed.py