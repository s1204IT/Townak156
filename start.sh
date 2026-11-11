#!/bin/sh
cd "$(dirname "$0")"
mkdir -p log

if [ ! -f certs/fullchain.pem ]; then
  env python3 make_cert.py
fi

pkill -f "python3 https.py" 2> /dev/null
sleep 1
nohup env python3 https.py > log/https.log 2>&1 &
echo $! >> log/https.pid

sudo -n systemctl stop tinydns 2> /dev/null
sudo -n systemctl reset-failed tinydns 2> /dev/null
sudo -n systemd-run --no-block --quiet --unit=tinydns --collect  --property=Restart=on-failure env python3 "$PWD/dns.py"

