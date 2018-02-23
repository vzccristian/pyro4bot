#!/bin/bash

##
# Instrucciones
#
# sshpass: sudo apt-get install sshpass
# Cambiar variable $red , $passSudo y $passRobot
# chmod +x yakuake-pyro-eduroam.sh
#
# Ejecutar:
# ./yakuake-pyro-eduroam.sh
##

red="158.49.247.0"
passSudo="PASS"
passRobot="PASS"

clear

echo -e "-----------------------------"
echo -e " Script lanzamiento Pyro4BOT"
echo -e "-----------------------------"
echo -e " Cristian Vazquez Cordero"
echo -e "-----------------------------"
echo -e "RED: $red"
echo -e "-----------------------------\n"
echo "Abriendo pestañas..."

INITIAL_ID=`qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.activeSessionId`
qdbus org.kde.yakuake /yakuake/tabs org.kde.yakuake.setTabTitle $INITIAL_ID 'Lanzando-script'

#client
echo "[1] Directorio pyro4bot/developing"
qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.addSession
sess=`qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.activeSessionId`

qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.runCommand 'cd ~/pyro4bot/developing'

qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.runCommand "clear"

qdbus org.kde.yakuake /yakuake/tabs org.kde.yakuake.setTabTitle $sess 'cliente'

echo "----------------------------------------------"

#bot
echo "[2] Terminal 1 para pyro4bot"
echo "- Buscando robot..."

ip=$(echo -e "$passSudo\n" | sudo -S  nmap -sP $red/24 | awk '/^Nmap/{ip=$NF}/B8:27:EB/{print ip}' | sed "s/(//" | sed "s/)//" | tail -1)
echo $ip

emptyIp="no"
if [ "$ip" = "" ]; then
	emptyIp=""
	read -p "Fallo al encontrar robot. Introducir IP: " ip
else
	echo "- IP conseguida: $ip"
fi

qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.addSession
sess=`qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.activeSessionId`

qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.runCommand "sshpass -p $passRobot  ssh -o StrictHostKeyChecking=no -X pi@$ip"

qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.runCommand "clear"

qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.runCommand "cd td/developing/"

qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.runCommand "clear"

qdbus org.kde.yakuake /yakuake/tabs org.kde.yakuake.setTabTitle $sess 'bot'

echo "----------------------------------------------"
sleep 1

#bot2
echo "[3] Terminal 2 para pyro4bot: NameServer"
qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.addSession
sess=`qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.activeSessionId`

qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.runCommand "sshpass -p $passRobot ssh -o StrictHostKeyChecking=no -X pi@$ip"

qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.runCommand "clear"

qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.runCommand "pyro4-ns -n $ip"

qdbus org.kde.yakuake /yakuake/tabs org.kde.yakuake.setTabTitle $sess 'nameserver'

echo "----------------------------------------------"

if [ "$emptyIp" = "" ]; then
	read -p "Pulsa para salir..." pulsa
else
	echo "Saliendo..."
	COUNTER=10
	while [  $COUNTER -gt 0 ]; do
			 echo $COUNTER
			 let COUNTER=COUNTER-1
			 sleep 1
	done
fi
echo "Saliendo..."

qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.removeSession $INITIAL_ID
