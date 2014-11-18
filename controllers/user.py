# -*- coding: utf-8 -*-


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    if request.args(0) == 'profile':
        response.view = 'user/profile.html'
        response.title = T('Profile')+'...'
    return dict(form=auth())



@auth.requires(auth.has_membership(role=ADMIN_ROLE))
def auth_user():
    action = request.args(0) or ''

    if action == '':
        content = app_crud_grid(db.auth_user)
    else:
        attr = dict()
        if action == 'new':
            attr['next'] = URL(c='user', f='auth_user', args=['edit'])+'/[id]'
        else:
            next = URL(c='user', f='auth_user')

        content = app_crud(db.auth_user, **attr)
    return dict(content=content)


@auth.requires(auth.has_membership(role=ADMIN_ROLE))
def auth_group():
    action = request.args(0) or ''

    if action == '':
        content = app_crud_grid(db.auth_group)
    else:
        content = app_crud(db.auth_group, **dict(next=URL(c='user', f='auth_group')))
    return dict(content=content)


def auth_groups():
    owner_table = getlist(request.args, 0)
    owner_key  = getlist(request.args, 1)
    if not (owner_table and owner_key and owner_key.isdigit()):
        response.view = 'others/gadget_error.html'        
        return dict(msg='access control groups dont work!')

    def getContentLocal():
        if owner_table == 'user':
            return [(row.auth_group.id, row.auth_group.role, row.auth_membership.id or 0) for row in 
                db().select(db.auth_group.ALL, db.auth_membership.id, 
                    left=db.auth_membership.on((db.auth_membership.group_id==db.auth_group.id) & (db.auth_membership.user_id == int(owner_key))))]
        else:
            return [(row.auth_user.id, '%(first_name)s %(last_name)s' % row.auth_user, row.auth_membership.id or 0) for row in 
                db().select(db.auth_user.ALL, db.auth_membership.id, 
                    left=db.auth_membership.on((db.auth_membership.user_id==db.auth_user.id) & (db.auth_membership.group_id == int(owner_key))))]

    content = getContentLocal()
    fields = [Field('record_'+str(k), 'boolean') for k, d, m in content]
    buttons = [INPUT(_type='submit', _value=T('Connect'), _class='btn')]
    form = SQLFORM.factory(*fields, buttons=buttons)
    if form.process(formname='auth_groups_form').accepted:
        for k, d, m in content:
            user_id, group_id = k, int(owner_key)
            if owner_table == 'user':
                user_id, group_id = int(owner_key), k

            checked = form.vars.get('record_'+str(k), False)
            if checked != (m>0):
                if checked:
                    db.auth_membership.insert(user_id=user_id, group_id=group_id)
                else:
                    db(db.auth_membership.id==m).delete()
        content = getContentLocal()
    return dict(form=form, content=content)
