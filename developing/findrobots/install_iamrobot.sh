#!/bin/bash
#eol=lf
path=`pwd`
sudo cp $path/iamrobot.service  /lib/systemd/system/iamrobot.service
sudo cp $path/iamrobot.py  /lib/systemd/system/iamrobot.py
sudo chmod 644 /lib/systemd/system/iamrobot.service
sudo chmod 644 /lib/systemd/system/iamrobot.py
sudo chmod +x /lib/systemd/system/iamrobot.py
sudo systemctl daemon-reload
sudo systemctl enable iamrobot.service
sudo systemctl start iamrobot.service
