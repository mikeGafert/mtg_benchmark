#!/bin/bash
source /var/www/vhosts/mtgbenchmark.com/httpdocs/env/bin/activate
exec gunicorn -w 4 -b 127.0.0.1:8000 run:app

