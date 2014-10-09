# -*- coding: utf-8 -*-

@auth.requires(lambda: auth_has_access())
def index():
    session.project = 'entries'
    return dict()


from onx_views import ONXFORM 
@auth.requires(lambda: auth_has_access())
def customer():
    content = ONXFORM.make(db.customer)
    return content


