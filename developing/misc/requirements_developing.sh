sudo add-apt-repository ppa:webupd8team/atom
sudo apt update
sudo apt install python-pip
sudo apt install atom
sudo apt install python-opencv
apm install teletype
pip2.7 install -r "requirements.txt"
sudo apt install git
Yellow='\033[0;33m'
echo "${Yellow}Quieres instalar Spotify? [y/n]"
read val
if [ val="y" ]
then
 snap install spotify
  echo "${Yellow} spotify instalado"
else
    echo "${Yellow} xd"
  fi
