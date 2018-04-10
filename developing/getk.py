<<<<<<< HEAD
import logging

class ColorFormatter(logging.Formatter):

    def color(self, level=None):
        codes = {\
            None:       (0,   0),
            'DEBUG':    (0,   2), # gris
            'INFO':     (0,   0), # normal
            'WARNING':  (1,  34), # azul
            'ERROR':    (1,  31), # rojo
            'CRITICAL': (1, 101), # negro, fondo rojo
            }
        return (chr(27)+'[%d;%dm') % codes[level]

    def format(self, record):
        retval = logging.Formatter.format(self, record)
        return self.color(record.levelname) + retval + self.color()


console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(ColorFormatter('    %(levelname)s[%(name)s]: %(message)s'))
logging.getLogger().addHandler(console)

logging.debug('mensaje para depuracion')
logging.info('informacion')
logging.warning('el que avisa no es traidor')
logging.error('un errorcillo')
logging.critical('y la liaste parda')
=======
from time import sleep
from colorama import Cursor, init, Fore
init()
print("Copiando archivos... ")
for arch in ["111", "222", "333", "444", "555"]:
    sleep(1)
    print(Cursor.UP(1)+Cursor.FORWARD(20)+Fore.YELLOW+str(arch))

print(Cursor.POS(25,2) + Fore.GREEN + ">>> Proceso finalizado")
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
