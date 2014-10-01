# -*- coding: utf-8 -*-


@auth.requires_login()
def tag():
    response.view = 'others/generic_crud.html'
    action = request.args(0) or ''

    if action == '':
        content = app_crud_grid(db.tag, controller=request.controller, function=request.function)
    else:
        content = app_crud(db.tag)
    return dict(content=content)


def tag_data():
    data = []
    for row in db(db.tag.id > 0).select(orderby=db.tag.name):
        data.append(row.name)
        
    return response.json(data)