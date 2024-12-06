#!/bin/bash

pybabel compile -d locales/
uwsgi uwsgi.ini