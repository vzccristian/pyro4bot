#!/usr/bin/env python
# coding=utf-8

import re
import requests
import os
from termcolor import cprint
import start_pyro4bot
import argparse

def error_print(x):
    cprint(x, 'red')

def create_from_template(*args):
    for a in args:
        try:
            f = open('./misc/component_template.py', "r")
            doc = open('./misc/documentation_template.md', "r")
        except:
            error_print("[ERROR] The templates doesn't exists")
            error_print("[ERROR] There shoud be component_template.py and documentation_template.md")
            break
        outf = re.sub('<TEMPLATE>', a, "".join(f.readlines()))
        outdoc = re.sub('<TEMPLATE>', a, "".join(doc.readlines()))
        newf = open("./node/sensors/" + a + ".py", "w")
        newdoc = open("./node/sensors/" + a + ".md", "w")
        newf.write(outf)
        newdoc.write(outdoc)
        f.close()
        doc.close()
        newf.close()
        newdoc.close()

def component_repo_list():
    components = requests.get('https://api.github.com/repos/vzccristian/pyro4bot/contents/developing/node/sensors')
    return [str(i['name']) for i in components.json() if i['name'][-3:] == ".py"]

def component_list():
    return [i for i in os.listdir("./node/sensors/") if i[-3:] == ".py"]

def compare_components(comp=component_repo_list()):
    return list(set(comp) - set(component_list()))
    
def install_components(comp=component_repo_list()):
    for i in compare_components(comp):
        r = requests.get("https://raw.githubusercontent.com/vzccristian/pyro4bot/developing/developing/node/sensors/"+i, allow_redirects=True)
        direc = "./node/sensors/"
        print direc + i
        open(direc+i, 'wb').write(r.content)
    
def install_components_from_json(json):
    error_print("[ERROR] NOT YET")

def help():
    print("\nusage: [options] inputs\n")
    print("-cc, --create-component *component_names       create a component from template")
    print("-i, --install-components [JSON]                download components from the repo")
    print("-s, --start-pyro4bot [JSON]                    starts pyro4bot")
    pass 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("create_component", "-cc", help="create a component from template", action='store_true', type=str)
    parser.add_argument("install_components", "-i", help="install the components needed to create the JSON's robot", type=str)
    parser.add_argument("start", "-s", help="starts pyro4bot", type=str)
    parser.add_argument("value")
    args = parser.parse_args()
    if args.create_component:
        if args.value:
            create_from_template(args.value)
        else:
            error_print("[ERROR] At least 1 valor needed to create a component from template")
    elif args.install_components:
        if args.value:
           install_components_from_json(args.value)
        else:
            inp = raw_input("You didn't input any parameters. "
                      "Do you want to install all components of the repository?[y/n]")
            if inp.lower() == 'y':
                install_components()
    elif args.start:
            if args.value:
                start_pyro4bot.start_pyro4bot(args.value)
            else:
                start_pyro4bot.start_pyro4bot()



if __name__ == '__main__':
    main()
