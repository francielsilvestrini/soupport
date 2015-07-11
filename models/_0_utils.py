#!/usr/bin/env python
# -*- coding: utf-8 -*-

SMALL = lambda x, **kwargs: XML(TAG.small(x, **kwargs).xml())
SUP = lambda x, **kwargs: XML(TAG.sup(x, **kwargs).xml())

class Utils(object):

    @staticmethod
    def url_vars_remove(remove_navegate=True):
        keys =  ['_signature', 'origin', 'amp']
        if remove_navegate:
            keys +=  ['next', '_next', 'previous', '_previous']
        return keys

    #loading = DIV([DIV(_id="fountainG_%s"%i, _class="fountainG") for i in range(8)], _id="fountainG")

    @staticmethod
    def url_vars(vars, remove=None, add=None, remove_navegate=True):
        new_vars = vars.copy()
        remove_keys = list(Utils.url_vars_remove(remove_navegate=remove_navegate))
        if remove:
            remove_keys += remove
        for k in remove_keys:
            if k in new_vars:
                del new_vars[k]

        if add:
            new_vars.update(add)
        return new_vars

    @staticmethod
    def url(c=None, f=None, args=None, vars=None, clear_vars=False, url_encode=True, \
            anchor=''):
        if clear_vars:
            new_vars = vars
        else:
            new_vars = Utils.url_vars(request.get_vars, add=vars)

        url = URL(c=c, f=f, args=args, vars=new_vars, url_encode=url_encode, \
            anchor=anchor)
        return url

    @staticmethod
    def href_back_or(default):
        href = request.get_vars.get('previous') or request.env.get('HTTP_REFERER')
        if not href:
            href = default
        return href

    @staticmethod
    def url_previous():
        return Utils.href_back_or(response.app_home)

    @staticmethod
    def is_redirect(e):
        return str(e) == '303 SEE OTHER'


    @staticmethod
    def url_current():
        return URL(args=request.args, vars=request.get_vars)

    @staticmethod
    def logger(name):
        logger = logging.getLogger(request.application+'/'+name)
        logger.setLevel(logging.DEBUG)
        return logger


#------------------------------------------------------------------------------
class DBUtils(object):

    @staticmethod
    def owner_fields():
        fields = db.Table(current.db, 'owner',
            Field('owner_table', 'string', label=T('Owner Table'),
                writable=False, readable=False),
            Field('owner_key', 'string', label=T('Owner Key'),
                writable=False, readable=False),
            Field('owner_link', 'string', label=T('Owner Link'),
                writable=False, readable=False),
        )
        return fields

    @staticmethod
    def signature_fields():
        def local_default_user():
            if auth.is_logged_in():
                return auth.user_id
            else:
                return None

        signature = db.Table(db, 'signature',
            Field('created_on', 'datetime', label=T('Criado em'),
                default=request.now, writable=False, readable=False),
            Field('created_by', db.auth_user, label=T('Criado por'),
                default= local_default_user, writable=False, readable=False),
            Field('updated_on', 'datetime', label=T('Alterado em'),
                update=request.now, writable=False, readable=False),
            Field('updated_by', db.auth_user, label=T('Alterado por'),
                update=local_default_user, writable=False, readable=False),
            Field('sender', 'string', label=T('Remetente (API)'),
                writable=False, readable=False),
            )
        return signature

    @staticmethod
    def field_repr(field, value, row):
        try:
            if field.type.startswith('reference '):
                rtable = field.type.split()[1]
                table =  db[rtable]
                table_format = table._format
                if isinstance(table_format, str):
                    rep = table_format % table[value]
                else:
                    rep = table._format(table[value])
            else:
                rep = represent(field, value, row)
            if str(rep) == 'None':
                rep = ' '
            return rep
        except:
            return value

    @staticmethod
    def row_repr(row, table, ignore=None):
        row.repr = Dict()
        row.label = Dict()
        for f in table:
            if ignore and f.name in ignore:
                row.repr[f.name] = row[f.name]
            else:
                row.repr[f.name] = DBUtils.field_repr(f, row[f.name], row)
            row.label[f.name] = f.label
        return row

    @staticmethod
    def default_values(table):
        values = {}
        for fname in table.fields:
            if not table[fname].default is None:
                if callable(table[fname].default):
                    values[fname] = table[fname].default()
                else:
                    values[fname] = table[fname].default
        return values

    @staticmethod
    def copydata(src, dest, fields):
        for k in fields:
            if src.has_key(k):
                dest[k] = src[k]
        return dest

    @staticmethod
    def last_id(table, query):
        max = table['id'].max()
        max_id = db(query).select(max).first()[max]
        return max_id

    @staticmethod
    def sum_field(field, query):
        sum = field.sum()
        sum_result = db(query).select(sum).first()[sum]
        return sum_result

    @staticmethod
    def str_date(date):
        if date:
            return date.strftime('%d-%m-%Y')
        return None

    @staticmethod
    def repr_currency(value, decimals=2):
        fmt = '{:10.%sf}'%decimals
        wrap = SPAN(SPAN('R$', _class='symbol'), SPAN(fmt.format(value), _class='value'), _class='currency')
        return wrap


#------------------------------------------------------------------------------
class CAS(object):

    controller = 'cas'

    @staticmethod
    def has_access(c=request.controller, f=request.function):
        #if auth.user.username == Constants.SUPER_USER:
        #    return True

        if auth.has_membership(role=Constants.ADMIN_ROLE[0]):
            return True
        # é o contrario de permitido, se tiver significa bloqueado
        return not auth.has_permission(c,f)

    @staticmethod
    def init():
        # auth.settings.extra_fields['auth_user'] = [
        #     Field('job_title', 'string', label=T('Job Title')),
        #     Field('photo', 'upload', label=T('Photo'), uploadfolder=UPLOAD_URLS['profile'], autodelete=True),
        #     Field('phone', 'string', label=T('Phone')),
        #     Field('birthday', 'date', label=T('Birthday')),
        #     Field('about', 'text', label=T('About Me')),
        #     ]
        auth.define_tables(username=True, signature=False)

        row = db(db.auth_group.role==Constants.ADMIN_ROLE[0]).select().first()
        if row:
            group_id = row.id
        else:
            group_id = db.auth_group.insert(role=Constants.ADMIN_ROLE[0], description=Constants.ADMIN_ROLE[1])

        if db(db.auth_user.username == Constants.SUPER_USER).count() == 0:
            values = DBUtils.default_values(db.auth_user)
            values.update(Constants.SUPER_USER_DEF)
            user_id = db.auth_user.insert(**values)
            auth.add_membership(group_id, user_id)

        if db(db.auth_user.username == Constants.ADMIN_USER).count() == 0:
            values = DBUtils.default_values(db.auth_user)
            values.update(Constants.ADMIN_USER_DEF)
            #values['password'] = db.auth_user.password.validate(Constants.ADMIN_USER_PASS)[0]
            user_id = db.auth_user.insert(**values)
            auth.add_membership(group_id, user_id)

        auth.settings.login_url = URL(c='cas', f='login')
        auth.settings.login_next = response.app_home
        auth.settings.logout_next = auth.settings.login_url
