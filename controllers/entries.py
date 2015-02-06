# -*- coding: utf-8 -*-

@auth.requires(lambda: auth_has_access())
def index():
    session.project = 'entries'
    session.breadcrumbs.reset(T('Entries'), current_url())
    return dict()


@auth.requires(lambda: auth_has_access())
def person():
    db.person.note.readable = request.args(0) == 'delete'
    content = ONXFORM.make(db.person)
    breadcrumbs_add()
    return content


@auth.requires(lambda: auth_has_access())
def platform():
    content = ONXFORM.make(db.platform)
    breadcrumbs_add()
    return content

