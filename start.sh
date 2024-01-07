#!/usr/bin/env sh

service nginx start

uwsgi --ini uwsgi.ini
