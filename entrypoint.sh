#!/bin/bash

python manage.py run_workers&
celery -A config worker -l INFO
