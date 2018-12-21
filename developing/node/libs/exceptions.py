

class Errornode(Exception):
    def __init__(self, error):
        self.error = error
        print(self.error)
