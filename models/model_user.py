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
        def _auth_user_default():
            a = globals().get('auth')
            if a and a.user_id > 0:
                return a.user_id
            else:
                return None

        sf = db.Table(db, 'signature',
            Field('oplink', 'string', label=T('Op Link'), default=uuid.uuid4, writable=False, readable=False),
            Field('created_on', 'datetime', default=request.now, writable=False, readable=False),
            Field('created_by', db.auth_user, default=_auth_user_default, writable=False, readable=False),
            Field('updated_on', 'datetime', update=request.now, writable=False, readable=False),
            Field('updated_by', db.auth_user, update=_auth_user_default, writable=False, readable=False))

        db._common_fields.append( sf )


        row = db(db.auth_group.role==Settings.ADMIN_ROLE).select().first()
        if row:
            group_id = row.id
        else:
            group_id = db.auth_group.insert(role=Settings.ADMIN_ROLE, description=T('Admin'))

        if db(db.auth_user.username == Settings.ADMIN_ROLE).count() == 0:
            defaults = table_default_values(db.auth_user)
            defaults['first_name'] = 'Admin'
            defaults['last_name'] = 'Admin'
            defaults['email'] = 'admin@admin.app'
            defaults['username'] = Settings.ADMIN_ROLE
            defaults['password'] = db.auth_user.password.validate(Settings.ADMIN_ROLE)[0]
            user_id = db.auth_user.insert(**defaults)
            auth.add_membership(group_id, user_id)

        if db(db.auth_user.username == Settings.SUPER_USER).count() == 0:
            defaults = table_default_values(db.auth_user)
            defaults['first_name'] = Settings.SUPER_USER
            defaults['last_name'] = Settings.SUPER_USER
            defaults['email'] = 'desenv@onnixsistemas.com.br'
            defaults['username'] = Settings.SUPER_USER
            defaults['password'] = db.auth_user.password.validate(Settings.SUPER_USER_PASS)[0]
            user_id = db.auth_user.insert(**defaults)
            auth.add_membership(group_id, user_id)
        return


def auth_has_access(c=request.controller, f=request.function):
    try:
        if auth.user.username == Settings.SUPER_USER:
            return True

        #valida se menu selecionda é de algum produto contratado
        menu_name = '%s_%s' % (c, f)
        menu = response.unique_menu.get(menu_name)
        if not menu:
            auth.settings.on_failed_authorization = URL(c='activity', f='menu_access', vars=dict(menu=menu_name))
            return False

        #valida o contrato
        if response.contract:
            if response.contract['result']['code'] > 100:
                auth.settings.on_failed_authorization = URL(c='activity', f='licence')
                return False

            is_valid = False
            for menu_prj in menu.projects:
                product = response.contract['items'].get(menu_prj)
                if product:
                    is_valid = product['result']['code'] == 100

            if not is_valid:
                auth.settings.on_failed_authorization = URL(c='activity', f='licence', vars=dict(menu=menu_name))
                return False

        if auth.has_membership(role=Settings.ADMIN_ROLE):
            return True
        # é o contrario de permitido, se tiver significa bloqueado
        return not auth.has_permission(c,f)
    except Exception, e:
        from onx_log import onx_logger
        onx_logger().error(str(e))
        return True
