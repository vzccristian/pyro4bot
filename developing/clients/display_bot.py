import Pyro4
from node.libs import utils
from clients._client_robot import ClientRobot
def main():
    bot = ClientRobot("display_bot")
    bot.display.set_image(open("z.jpg", "rb").read())
if __name__ == '__main__':
    main()
