#!/usr/bin/env python3
""" PYRO4BOT Generator launcher.
    This program generates the first directories and files that are needed to create your own pyro4bot robot.

Launcher file
"""
import sys
import os


# sys.path.append("../node/libs")


def update_robot():
    """ It checks and updates the directories and files needed to run the robot.
    this only can be used once the user has described its robot in the json file.
    _______________

    If the services and components of the robots are already in the repository, they will be downloaded.
    If not, the user must have developed the necessary files to handle those dependencies of the robots.
    If neither of them are completed, this will show an error message to the user.
    """
    pass  # TODO


def create_robot(jsonbot):
    """ The first execution of this program will create the structure, files and directories needed to a
    pyro4bot robot
    """
    if not os.path.exists('services'):
        os.makedirs('services')
    if not os.path.exists('components'):
        os.makedirs('components')
    if not os.path.exists('clients'):
        os.makedirs('clients')
    pass  # TODO


if __name__ == "__main__":
    """ Main function of this program.
    It checks the argument passed to the program and generate the necessary files to each case,
    depending on the current development of the robot.
    ______________________
    The first time it is executed, it should be using only the argument 'robot_name' with the name of the robot;
    for example: python3 generate_robot.py robot_name
    
    The second time, it expects the user has already described the robot in the json file, and developed the 
    components and services needed in case they are not in the repository. Then, the execution should update the 
    directories like this: python3 generate_robot.py -update
    """
    # TODO
    try:
        if len(sys.argv) != 2:
            print("File was expected as argument.")
            os._exit(0)
        else:
            argument = sys.argv[1]
            if argument == '-update':
                update_robot()
            else:
                create_robot(argument)
    except IOError:
        print("The file can not be found: %s" % jsonbot)
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)
    except Exception:
        raise
