#!/usr/bin/env bash
sudo add-apt-repository ppa:webupd8team/atom
sudo apt update
sudo apt install python3-pip
sudo apt install atom
# sudo apt install python3-opencv
pip3 install opencv-python
pip3 install -r "requirements.txt"
sudo apt install git
sudo pip3 install green
