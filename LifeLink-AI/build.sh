#!/usr/bin/env bash
# Render build script for LifeLink AI.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_demo
