# -*- coding: utf-8 -*-
from onx_views import ONXFORM 


@auth.requires(lambda: auth_has_access())
def tag():
    content = ONXFORM.make(db.tag)
    breadcrumbs_add()
    return content


def tag_data():
    data = []
    for row in db(db.tag.id > 0).select(orderby=db.tag.name):
        data.append(row.name)
        
    return response.json(data)