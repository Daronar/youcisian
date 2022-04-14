#!/bin/sh
flake8 --exclude=tests/*,venv --ignore=E501
python -m pytest tests/