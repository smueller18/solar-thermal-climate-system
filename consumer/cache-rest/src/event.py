# -*- coding: utf-8 -*-

__author__ = u'Stephan Müller'
__copyright__ = u'2016, Stephan Müller'
__license__ = u'MIT'


class Event(object):
    def __init__(self):
        self.handlers = []

    def add(self, handler):
        self.handlers.append(handler)
        return self

    def remove(self, handler):
        self.handlers.remove(handler)
        return self

    def fire(self, sender, *args):
        for handler in self.handlers:
            handler(sender, *args)

    __iadd__ = add
    __isub__ = remove
