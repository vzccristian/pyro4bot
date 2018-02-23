
class Docstring(object):
    def __init__(self, object_name, doc=None):
        """Init Docstring."""
        self.name = object_name
        if not isinstance(doc, dict):
            self.doc = {}

    def update_key_value(self, key, value):
        """Update the docstring dictionary by key and value."""
        self.doc[key] = value

    def update_from_dict(self, d):
        """Update the dictionary of docstring by dictionary."""
        if isinstance(d, dict):
            # Copy is made in case the dictionary changes during the iteration
            self.doc.update(d.copy())
        else:
            print "Error. The parameter is not a dictionary"
            
    def __repr__(self):
        return repr(self.doc)
