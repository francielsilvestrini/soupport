# -*- coding: utf-8 -*-

class OnxUtils(object):

    @staticmethod
    def table_default_values(table):
        defaults = {}
        for fname in table.fields:
            if table[fname].default:
                if callable(table[fname].default):
                    defaults[fname] = table[fname].default()
                else:
                    defaults[fname] = table[fname].default
        return defaults
