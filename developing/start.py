#!/usr/bin/env python
# coding=utf-8

import start_pyro4bot
import misc.utils as u
import fire


class Start:

    def __init__(self):
        pass

    def help(self):
        print("\nusage: [options] inputs\n")
        print("-cc, --create-component *component_names       create a component from template")
        print("-i, --install-components [JSON]                download components from the repo")
        print("-s, --start-pyro4bot [JSON]                    starts pyro4bot")

    def create_component(self, *name):
        u.create_from_template(*name)

    def install_components(self, json=None):
        if json is not None:
            u.install_components_from_json(json)
        else:
            inp = raw_input("You didn't input any parameters. "
                            "Do you want to install all components of the repository?[y/n]\n")
            if inp.lower() == 'y':
                u.install_components()

    def start(self, name=None):
        start_pyro4bot.start_pyro4bot(name)


if __name__ == '__main__':
    fire.Fire(Start)
