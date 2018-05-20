import time
from _client_robot import ClientRobot


if __name__ == "__main__":
    print("Ejecutando cliente mirror...")

    bot = ClientRobot("master")
    # bot2 = ClientRobot("esclavo")

    print(bot.mirror.__docstring__())
    # print(bot2.ruedas.__docstring__())
    bot.mirror.set__vel()
    # bot2.ruedas.forward()
    time.sleep(3)
    bot.mirror.set__vel(mi=0, md=0)
