#!/usr/bin/bash

source myenv/bin/activate

python manage.py fetch_data

celery -A recipe_app worker -l info

celery -A recipe_app beat -l info

