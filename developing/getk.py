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
