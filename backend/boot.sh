#!/bin/sh
source venv/bin/activate

exec gunicorn -b :5000 --worker-class eventlet -w 3 --access-logfile - --error-logfile - manage:app