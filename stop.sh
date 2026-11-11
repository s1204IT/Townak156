#!/bin/sh
cd "$(dirname "$0")"

if [ -f log/https.pid ]; then
  kill "$(cat log/https.pid)" 2> /dev/null
  rm -f log/https.pid
fi
pkill -f "python3 https.py" 2> /dev/null

sudo -n systemctl stop tinydns 2> /dev/null
sudo -n systemctl reset-failed tinydns 2> /dev/null
