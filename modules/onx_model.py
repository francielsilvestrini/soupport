# -*- coding: utf-8 -*-

class ModelBase(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "Model: %s" % self.name

    def define_tables(self):
        return

    def create_defaults(self):
    	#print "Model: %s" % type(self).__name__
        return
