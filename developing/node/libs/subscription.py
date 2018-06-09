#!/usr/bin/env python

def dict_to_class(d):
    if ("_target" in d and "_target_attr" in d and "_subscripter_attr" in d and
        "_subscripter_password" in d):
        s = Subscription(d["_target"], d["_target_attr"], d["_subscripter_attr"], d["_subscripter_password"])
        s.subscripter_uri = d["_subscripter_uri"]
        s.subscripter = d["_subscripter"]
        s.id = d["_id"]
        return s
    else:
        return None

class Subscription(object):
    """ Class designed for subscription."""

    def __init__(self, target, target_attr, subscripter_attr=None, subscripter_password=None):
        self._target = target  # Destination proxy (target)
        self._target_attr = target_attr  # Target atribute
        self._subscripter_attr = subscripter_attr if (
            subscripter_attr is not None) else target_attr  # Susbcriber atribute
        self._subscripter_password = subscripter_password  # Subscriber password
        self._subscripter_uri = None  # Subscriber uri
        self._subscripter = None  # Subscriber proxy
        self._id = None

    def get(self):
        return self.__dict__

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value

    @property
    def target_attr(self):
        return self._target_attr

    @target_attr.setter
    def target_attr(self, value):
        self._target_attr = value

    @property
    def subscripter_attr(self):
        return self._subscripter_attr

    @subscripter_attr.setter
    def subscripter_attr(self, value):
        self._subscripter_attr = value

    @property
    def subscripter_password(self):
        return self._subscripter_password

    @subscripter_password.setter
    def subscripter_password(self, value):
        self._subscripter_password = value

    @property
    def subscripter_uri(self):
        return self._subscripter_uri

    @subscripter_uri.setter
    def subscripter_uri(self, value):
        self._subscripter_uri = value

    @property
    def subscripter(self):
        return self._subscripter

    @subscripter.setter
    def subscripter(self, value):
        self._subscripter = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    def __repr__(self):
        return ("[ID:{}], target: {}, target_attr: {}, subscripter_attr: {}, subscripter_password: {}, subscripter_uri: {}, subscripter: {}".format(self._id, self._target, self._target_attr, self._subscripter_attr, self._subscripter_password, self._subscripter_uri, self._subscripter))

    def __str__(self):
        return ("[ID:"+str(self._id)+"], target: " + str(self._target) + ", target_attr: " + str(self._target_attr) + ", subscripter_attr: " + str(self._subscripter_attr) + " , subscripter_password: " + str(self._subscripter_password)
                +", subscripter_uri: "+str(self._subscripter_uri)+", subscripter: "+str(self._subscripter))


if __name__ == '__main__':
    s = Subscription("usbserial", "LASER")
    s.id = 2
    print s
    s.id = 4
    print str(s)
    d = s.__dict__
    print dict_to_class(d)
