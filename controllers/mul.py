# -*- coding: utf-8 -*-

@auth.requires(lambda: auth_has_access())
def index():
    session.project = 'mul'
    return dict()

