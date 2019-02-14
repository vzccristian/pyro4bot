## Getting Started
### How to install _iamrobot_ as a service

Situate in the directory where you have the files _iamrobot.py, iamrobot.service,
install_iamrobot.sh_ and _findrobots.py_

Once you checked this, execute:
```
sudo sh install_iamrobot.sh
```

Then it should show:

``
Created symlink /etc/systemd/system/multi-user.target.wants/iamrobot.service -> /lib/systemd/system/iamrobot.service.
``

The service has already been installed, it works automatically when the system
is started.

##
You can stop, start or restart like any other system service:

```
sudo service iamrobot start
sudo service iamrobot restart
sudo service iamrobot stop
```


## Deployment
### How to search robots

Just open a terminal and execute **_findrobots.py_**

```
python3 findrobots.py
```
or (in case you configured your _python 3.x_ with just the _python_ alias):
```
python findrobots.py
```
