# How to install iamrobot as service

First, the default working directory is: /home/pi/PYRO4DIR/pyro4bot/developing/misc
You can change this directory in the path variable within the file install_iamrobot.sh

Make sure you have the file iamrobot.py and iamrobot.service in the directory
indicated in install_iamrobot.sh

Checked this, execute:

sudo sh install_iamrobot.sh

Then it should show:
Created symlink /etc/systemd/system/multi-user.target.wants/iamrobot.service -> /lib/systemd/system/iamrobot.service.

The service has already been installed, it works automatically when the system
is started.

You can stop, start or restart like any other system service:
sudo service iamrobot start
sudo service iamrobot restart
sudo service iamrobot stop

# How to search a robots

Just execute findrobots.py

python findrobots.py
