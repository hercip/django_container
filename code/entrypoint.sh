#!/bin/bash

cd /opt/up/vo

echo "Running migrations start"
python manage.py dbwait
echo "Running migrations done"

echo "Running migrations start"
python manage.py makemigrations
echo "Running migrations done"

echo "Running migrate start"
python manage.py migrate --no-input
echo "Running migrate done"

echo "Running command '$*'"
exec su -s /bin/zsh -c "$*"
