# -*- coding: utf-8 -*-


class UserModel(ModelBase):
    name = 'user'


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
        sf = db.Table(db, 'signature',
            Field('oplink', 'string', label=T('Op Link'), default=uuid.uuid4, writable=False, readable=False),
            Field('created_on', 'datetime', default=request.now, writable=False, readable=False),
            Field('created_by', db.auth_user, default=_auth_user_default, writable=False, readable=False),
            Field('updated_on', 'datetime', update=request.now, writable=False, readable=False),
            Field('updated_by', db.auth_user, update=_auth_user_default, writable=False, readable=False))

        db._common_fields.append( sf )

        if db(db.auth_user).isempty():
            row = db(db.auth_group.role==ADMIN_ROLE).select().first()
            if row:
                group_id = row.id
            else:
                group_id = db.auth_group.insert(role=ADMIN_ROLE, description=T('Admin'))

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
    if auth.has_membership(role=ADMIN_ROLE):
        return True
    # é o contrario de permitido, se tiver significa bloqueado
    return not auth.has_permission(c,f)

def _auth_user_default():
    a = globals().get('auth')
    if a and a.user_id > 0:
        return a.user_id
    else:
        return None
