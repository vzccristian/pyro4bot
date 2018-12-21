#!/usr/bin/env python


class Publication(object):
    """ Class designed for inclusion in the for publication and subscription.
    Publication
    """
    def __init__(self, data=None):
        self.data = data if data else {}

    def add_data(self, d):
        if isinstance(d, dict):
            self.data.update(d)
        else:
            print("Can not add to data. It should be a dictionary.")

    def update_key_value(self, key, value):
        if (key in list(self.data.keys())):
            self.data[key] = value
        else:
            self.add_data({key: value})

    def update_from_dict(self, d):
        if isinstance(d, dict):
            self.data.update(d.copy())
        else:
            print("Error. The parameter is not a dictionary")

    def get(self):
        return self.data
