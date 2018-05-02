#!/usr/bin/env python
"""PYRO4BOT Launcher.

Launcher file
"""
import node.robotstarter as robot
import sys
import os
import setproctitle
from node.libs import utils
import time
from termcolor import colored

if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            print("File was expected as argument.")
            os._exit(0)
        else:
            jsonbot = sys.argv[1]

        PROCESS = robot.starter(filename=jsonbot)

        setproctitle.setproctitle("PYRO4BOT." + PROCESS[0] + "." + "Console")
        ROB = utils.get_pyro4proxy(PROCESS[1], PROCESS[0])

        salir = True
        time.sleep(2)
        while salir:
            print colored("\n----\nComandos disponibles: \n* Doc \n* Status \n* Exit\n----\n", "green")
            cad = raw_input("{} ".format(colored(PROCESS[0] + ":", 'green')))
            if cad.upper() == "EXIT":
                ROB.shutdown()
                os.kill(PROCESS[3], 9)
                exit()
            if cad.upper() == "STATUS":
                ROB.print_process()
            if cad.upper() == "DOC":
                for k, v in ROB.__docstring__().items():
                    print(k)
                    print("\t" + str(v))
            if cad.upper() == "SALIR":
                salir = False
                exit()
    except IOError:
        print("The file can not be found: %s" % jsonbot)
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)
    except Exception:
        raise
