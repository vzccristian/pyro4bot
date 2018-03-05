#!/bin/bash
#eol=lf
path="/home/pi/PYRO4DIR/pyro4bot/developing/misc"
cp ./iamrobot.service  /lib/systemd/system/iamrobot.service
sudo chmod 644 /lib/systemd/system/iamrobot.service
chmod +x $path/findrobots/iamrobot.py
sudo systemctl daemon-reload
sudo systemctl enable iamrobot.service
sudo systemctl start iamrobot.service
