from time import sleep
from colorama import Cursor, init, Fore
init()
print("Copiando archivos... ")
for arch in ["111", "222", "333", "444", "555"]:
    sleep(1)
    print(Cursor.UP(1)+Cursor.FORWARD(20)+Fore.YELLOW+str(arch))

print(Cursor.POS(25,2) + Fore.GREEN + ">>> Proceso finalizado")
