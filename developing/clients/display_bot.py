import Pyro4
from node.libs import utils
from clients.nodeproxy import ClientNODERB
def main():
    bot = ClientNODERB("display_bot")
    bot.display.set_image(open("z.jpg", "rb").read())
if __name__ == '__main__':
    main()
