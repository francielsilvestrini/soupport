# -*- coding: utf-8 -*-


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