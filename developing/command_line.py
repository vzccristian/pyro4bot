#!/usr/bin/env python
# coding=utf-8
import re
import requests
import os
import sys
from termcolor import cprint

import start_pyro4bot

error_print = lambda x : cprint(x, 'red')
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
    print("\nUsage: [options] inputs\n")
    print("-cc, --create-component *component_names       create component from template")
    print("-i, --install-components [JSON]                download components from the repo")
    print("-s, --start-pyro4bot [JSON]                    starts pyro4bot")

def main():
    if len(sys.argv) == 1:
        help()
    else:
        if sys.argv[1] in ['-cc', '--create-component']:
            if len(sys.argv) > 2:
                create_from_template(sys.argv[2:])
            else:
                error_print("[ERROR] At least one value is needed to create a component from a template")
        elif sys.argv[1] in ['-i', '--install-components']:
            if len(sys.argv) == 3:
                install_components_from_json(sys.argv[2])
            elif len(sys.argv) == 2:
                install_components()
        elif sys.argv[1] in ['-h', '--help']:
            help()
        elif sys.argv[1] in ['-s', '--start-pyro4bot']:
            if len(sys.argv) == 3:
                start_pyro4bot.start_pyro4bot(sys.argv[2])
            else:
                start_pyro4bot.start_pyro4bot()


if __name__ == '__main__':
    main()
