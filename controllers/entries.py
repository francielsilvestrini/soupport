# -*- coding: utf-8 -*-
from onx_views import ONXFORM 


@auth.requires(lambda: auth_has_access())
def index():
    session.project = 'entries'
    session.breadcrumbs.reset(T('Entries'), current_url())
    return dict()


@auth.requires(lambda: auth_has_access())
def customer():
    db.customer.note.readable = request.args(0) == 'delete'
    content = ONXFORM.make(db.customer)
    breadcrumbs_add()
    return content


@auth.requires(lambda: auth_has_access())
def platform():
    content = ONXFORM.make(db.platform)
    breadcrumbs_add()
    return content

