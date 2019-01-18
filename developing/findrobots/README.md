# How to install iamrobot as service

Situate in the directory where you have the files iamrobot.py, iamrobot.service,
install_iamrobot.sh and findrobots.py

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

# How to search robots

Just execute findrobots.py

python3 findrobots.py
