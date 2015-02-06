# -*- coding: utf-8 -*-

@auth.requires_login()
def index():
    session.project = 'activity'
    session.breadcrumbs.reset(T('Activity'), current_url())

    if response.contract and response.contract['result']['code'] > 100:
        response.page_alerts.append((
        response.contract['result']['code'],
        T(response.contract['result']['message']),
        'error'))
    return dict()


def todo_box():
    form = SQLFORM.factory(
        db.activity_todo.content,
        )

    query = (db.activity_todo.created_by == auth.user_id)
    query &= (db.activity_todo.status == 'waiting')

    todo_lst = db(query).select()
    return dict(form=form, todo_lst=todo_lst)


def todo_method():
    if request.vars.get('done'):
        id = int(request.vars.done)
        db(db.activity_todo.id == id).update(status='done')
    elif request.vars.get('canceled'):
        id = int(request.vars.canceled)
        db(db.activity_todo.id == id).update(status='canceled')
    else:
        content = request.vars['content'] or 'To-Do Empty'
        defaults = table_default_values(db.activity_todo)
        defaults['content'] = content

        db.activity_todo.insert(**defaults)
    return


@auth.requires_login()
def licence():
    if request.vars.get('origin') != 'menu':
        session.project = 'activity'
        session.breadcrumbs.reset(T('Activity'), URL(f='index'))

    response.title = T('Licence')
    breadcrumbs_add(response.title)

    if response.contract['result']['code'] > 100:
        response.page_alerts.append((
            response.contract['result']['code'],
            T(response.contract['result']['message']),
            'error'))
    return dict()


@auth.requires_login()
def menu_access():
    response.title = T('Message')
    response.subtitle = ''
    response.view = 'others/message_error.html'
    breadcrumbs_add(response.title)

    menu_name = request.vars.get('menu', '')
    message = T('Menu item selected not found!')
    return dict(title=menu_name, message=message)
