#!/usr/bin/env python


class Token(object):
    """ Class designed for inclusion in the for publication and subscription.
    Token
    """
    def __init__(self, attribs=None):
        self.attribs = attribs if attribs else {}

    def add_attribs(self, d):
        if isinstance(d, dict):
            self.attribs.update(d)
        else:
            print "Can not add to Topics. It should be a dictionary."

    def update_key_value(self, key, value):
        if (key in self.attribs.keys()):
            self.attribs[key] = value
        else:
            self.add_attribs({key: value})

    def update_from_dict(self, d):
        if isinstance(d, dict):
            self.attribs.update(d.copy())
            # d_up = d.copy()
            # for k, value in d_up.iteritems():
            #     self.update_key_value(k, value)
        else:
            print "Error. The parameter is not a dictionary"

    def get_attribs(self):
        return self.attribs
