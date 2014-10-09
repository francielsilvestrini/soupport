# -*- coding: utf-8 -*-

from onx_model import ModelBase

class UserModel(ModelBase):

    def define_tables(self):
        auth.settings.extra_fields['auth_user']= [
            Field('job_title', 'string', label=T('Job Title')),
            Field('photo', 'upload', label=T('Photo'), uploadfolder=UPLOAD_URLS['profile'], autodelete=True),
            Field('phone', 'string', label=T('Phone')),
            Field('birthday', 'date', label=T('Birthday')),
            Field('about', 'text', label=T('About Me')),
            ]
        auth.define_tables(username=True, signature=False)
        return

    def create_defaults(self):
        if db(db.auth_user).isempty():
            row = db(db.auth_group.role=='admin').select().first()
            if row:
                group_id = row.id
            else:
                group_id = db.auth_group.insert(role='admin', description=T('Admin'))

            defaults = my_default_values(db.auth_user)
            defaults['first_name'] = 'Admin'
            defaults['last_name'] = 'Admin'
            defaults['email'] = 'admin@admin.app'
            defaults['username'] = 'admin'
            defaults['password'] = db.auth_user.password.validate('admin')[0]
            user_id = db.auth_user.insert(**defaults)

            auth.add_membership(group_id, user_id)
        return


def auth_has_access(c=request.controller, f=request.function): 
    if auth.has_membership(role='admin'):
        return True
    # é o contrario de permitido, se tiver significa bloqueado
    return not auth.has_permission(c,f)
