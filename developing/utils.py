import re
import requests
import os
import sys


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
        r = requests.get(
            "https://raw.githubusercontent.com/vzccristian/pyro4bot/developing/developing/node/sensors/" + i,
            allow_redirects=True)
        direc = "./node/sensors/"
        print direc + i
        open(direc + i, 'wb').write(r.content)


def install_components_from_json(json):
    error_print("[ERROR] NOT YET")
