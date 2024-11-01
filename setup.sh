#!/bin/bash

/usr/local/bin/python3.11 -m venv "venv"
source venv/bin/activate
pip install --upgrade pip
pip install pip-tools
pip-compile --output-file requirements.txt requirements.in
pip install -r requirements.txt
