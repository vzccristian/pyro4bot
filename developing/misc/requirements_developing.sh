#!/usr/bin/env bash
sudo add-apt-repository ppa:webupd8team/atom
sudo apt update
sudo apt install python3-pip
sudo apt install atom
# for a raspberry pi Zero, don't install opencv:
# for the robot, install:
sudo pip3 install opencv-contrib-python
pip3 install -r "requirements.txt"
sudo apt install git
sudo pip3 install green
