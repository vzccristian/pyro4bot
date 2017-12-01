import os
import inspect
import importlib


# We're going to work with absolute imports as it's just easier.
# We'll get something like "node.importer", we want "node.our_thing".
SERVICES_PKG = '.'.join(__name__.split('.')[:-1]) + '.services'
SERVICES_DIR = os.path.abspath(os.path.join(__file__, os.pardir, 'services'))


_classes = {}


print('Populating dictionary of available services...')
for f in os.listdir(SERVICES_DIR):
    name, ext = os.path.splitext(f)
    if ext == '.py' and name != '__init__':
        try:
            module = importlib.import_module(SERVICES_PKG + '.' + name)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj):
                    _classes[name] = obj
                    print('Added class "%s"' % name)
        except ImportError as e:
            print('Loading module "%s" failed due to %s' % (name, str(e)))


def get_class(name):
    """Given the name of a class, returns its class, or None if not found"""
    # TODO If module not found, pull it from the repository?
    return _classes.get(name, None)


def import_class(name):
    """Given the name of a class, adds its class to the list of globals"""
    if isinstance(name, str):
        cls = get_class(name)
        if cls:
            globals[name] = cls
        else:
            print('Failed to import', name)
    else:
        for x in name:
            cls = get_class(x)
            if cls:
                globals[x] = cls
            else:
                print('Failed to import', x)
