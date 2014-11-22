# -*- coding: utf-8 -*-
from onx_views import ONXFORM 


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
    def do_manager_extra_links(self, row):
        menu = [A(
                SPAN(T('Groups')),
                _href=URL(f='groups', args=['auth_user', row.id]))]
        return menu

    db.auth_user.photo.readable=False
    db.auth_user.birthday.readable=False
    db.auth_user.about.readable=False

    oform = ONXFORM(db.auth_user)
    oform.customize.on_manager_extra_links = do_manager_extra_links
    content = oform.get_current_action()

    breadcrumbs_add()   
    return content


@auth.requires(auth.has_membership(role=ADMIN_ROLE))
def auth_group():
    def do_manager_extra_links(self, row):
        menu = [A(
                SPAN(T('Members')),
                _href=URL(f='groups', args=['auth_group', row.id]))]
        return menu

    oform = ONXFORM(db.auth_group)
    oform.customize.on_manager_extra_links = do_manager_extra_links
    content = oform.get_current_action()

    breadcrumbs_add()    
    return content


@auth.requires(auth.has_membership(role=ADMIN_ROLE))
def groups():
    owner_table = getlist(request.args, 0)
    owner_key  = getlist(request.args, 1)
    if not (owner_table and owner_key and owner_key.isdigit()):
        response.view = 'others/gadget_error.html'        
        return dict(msg='access control groups dont work!')

    def get_content_local():
        if owner_table == 'auth_user':
            return [(row.auth_group.id, row.auth_group.role, row.auth_membership.id or 0) for row in 
                db().select(db.auth_group.ALL, db.auth_membership.id, 
                    left=db.auth_membership.on((db.auth_membership.group_id==db.auth_group.id) & (db.auth_membership.user_id == int(owner_key))))]
        else:
            return [(row.auth_user.id, '%(first_name)s %(last_name)s' % row.auth_user, row.auth_membership.id or 0) for row in 
                db().select(db.auth_user.ALL, db.auth_membership.id, 
                    left=db.auth_membership.on((db.auth_membership.user_id==db.auth_user.id) & (db.auth_membership.group_id == int(owner_key))))]

    def get_owner_name():
        if owner_table == 'auth_user':
            name = db.auth_user._format % db(db.auth_user.id == int(owner_key)).select().first()
        else:
            name = db.auth_group._format % db(db.auth_group.id == int(owner_key)).select().first()
        return name

    content = get_content_local()
    fields = [Field('record_'+str(k), 'boolean') for k, d, m in content]

    buttons = [
        INPUT(_type='submit', _value=T('Connect'), _class='btn btn-success'),
        A(T('Cancel'), _class='btn', _href=URL(f=owner_table)),
        ]    

    form = SQLFORM.factory(*fields, buttons=buttons)
    if form.process(formname='auth_groups_form').accepted:
        for k, d, m in content:
            user_id, group_id = k, int(owner_key)
            if owner_table == 'auth_user':
                user_id, group_id = int(owner_key), k

            checked = form.vars.get('record_'+str(k), False)
            if checked != (m>0):
                if checked:
                    db.auth_membership.insert(user_id=user_id, group_id=group_id)
                else:
                    db(db.auth_membership.id==m).delete()
        redirect(URL(f=owner_table))
    response.title = T('Groups') if owner_table == 'auth_user' else T('Members')
    response.subtitle = get_owner_name()
    breadcrumbs_add(title=response.title)    
    return dict(form=form, content=content)
