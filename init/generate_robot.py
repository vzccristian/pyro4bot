#!/usr/bin/env python3
""" PYRO4BOT Generator launcher.
    This program generates the first directories and files that are needed to create your own pyro4bot robot.

Launcher file
"""
import os
import sys
import fileinput
import urllib.request

__url__ = 'https://raw.githubusercontent.com/BertoSerrano/pyro4bot_components/develop/'


def update_robot():
    """ It checks and updates the directories and files needed to run the robot.
    this only can be used once the user has described its robot in the json file.
    _______________

    If the services and components of the robots are already in the repository, they will be downloaded.
    If not, the user must have developed the necessary files to handle those dependencies of the robots.
    If neither of them are completed, this will show an error message to the user.
    """
    # TODO
    pass


def __create_template__(url_module, local_path):
    """ It creates the templates for the components that must be develop """
    file = local_path + 'Template.py'
    file_url = __url__ + url_module + 'Template.py'
    urllib.request.urlretrieve(file_url, file)


def __create_json__(path, bot_name):
    """ It creates the json file for the robot from a template """
    json_bot_file = path + bot_name + '.json'
    json_url = __url__ + 'init/bot_template.json'
    urllib.request.urlretrieve(json_url, json_bot_file)
    try:
        for line in fileinput.input([json_bot_file], inplace=True):
            print(line.replace('botname', bot_name), end='')
    except IOError:
        print("There has been an error with the template con the bot")
        raise


def create_robot(bot_name):
    """ The first execution of this program will create the structure, files and directories needed to a
    pyro4bot robot
    """
    path = 'robots/'
    if not os.path.exists(path):
        os.makedirs(path)
    path = path + bot_name + '/'
    if not os.path.exists(path):
        os.makedirs(path)
    for module in ['services/', 'components/', 'clients/']:
        if not os.path.exists(path + module):
            os.makedirs(path + module)
            __create_template__(module, path + module)
    __create_json__(path, bot_name)


if __name__ == "__main__":
    """ Main function of this program.
    It checks the argument passed to the program and generate the necessary files to each case,
    depending on the current development of the robot.
    
    The first time it is executed, it should be using only the argument 'robot_name' with the name of the robot;
    for example: python3 generate_robot.py robot_name
    
    The second time, it expects the user has already described the robot in the json file, and developed the 
    components and services needed in case they are not in the repository. Then, the execution should update the 
    directories like this: python3 generate_robot.py -update
    """
    try:
        if len(sys.argv) != 2:
            print("File was expected as argument.")
            os._exit(0)
        else:
            argument = sys.argv[1]
            if argument == '-update':
                update_robot()
            else:
                argument.replace('.json', '')
                create_robot(argument)
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)
    except Exception:
        raise
