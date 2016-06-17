#!/bin/bash
git pull
pip install -r requirements.txt
/home/hackathon/.virtualenvs/circus/bin/circusctl stop
ps aux | grep -i circus[d] | awk {'print $2'} | xargs kill -9
/home/hackathon/.virtualenvs/circus/bin/circusd circus/circus.ini --daemon
