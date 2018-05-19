
import time
from _client_robot import ClientRobot


if __name__ == "__main__":
    print("Ejecutando cliente mirror...")

    bot = ClientRobot("master")
    print(bot.mirror.__docstring__())

    bot.mirror.set__vel()
    time.sleep(5)
    bot.mirror.set__vel(mi=0, md=0)
