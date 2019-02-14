from ._client_robot import ClientRobot


def main():
    bot = ClientRobot("display_bot")
    # bot.WSEPaper.print_image(open("/home/jmagundezg/Escritorio/a.jpg").read())
    bot.WSEPaper.set_text("1 2", font=90)


if __name__ == '__main__':
    main()
