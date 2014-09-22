# -*- coding: utf-8 -*-


def todo_box():
    form = SQLFORM.factory(
        db.activity_todo.content,
        db.activity_todo.url
        )

    query = (db.activity_todo.created_by == auth.user_id)
    query &= (db.activity_todo.status == 'waiting')
    
    todo_lst = db(query).select()
    return dict(form=form, todo_lst=todo_lst)


def todo_post():
    content = request.vars['content'] or 'ToDo Empty'
    url = request.vars['url'] or ''

    defaults = table_default_values(db.activity_todo)
    defaults['content'] = content
    defaults['url'] = url

    db.activity_todo.insert(**defaults)

        # response.js = '''
        #    web2py_component('%(url_list)s','todo-container');
        #    make_popover(false);
        #''' % dict(
        #    url_list=URL(f='todo_list.load'))

    return