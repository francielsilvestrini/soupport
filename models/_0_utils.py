# -*- coding: utf-8 -*-

response.header_files = dict()
response.footer_files = dict()

from gluon.custom_import import track_changes
track_changes(True)

## GLOBAL IMPORTS ##
from gluon.tools import prettydate
## END GLOBAL IMPORTS ##


SMALL = lambda x, **kwargs: XML(TAG.small(x, **kwargs).xml())
SUP = lambda x, **kwargs: XML(TAG.sup(x, **kwargs).xml())


from os import path
UPLOAD_URLS = {
    'profile': path.join(request.folder,'uploads','profile'),
    'attachments': path.join(request.folder,'uploads','attachments'),
}

def getlist(x, index, default=None):
    return x[index] if len(x) > index else default


def alert_gedgat_error(msg):
    alert = DIV(
        BUTTON('&times;', _type='button', _class='close', **{'_data-dismiss':'alert'}),
        STRONG(T('ERROR!')),
        SPAN(T(msg)),
        _class='alert alert-error')
    return alert


def field_rep(field, value, row):

    def format(table, record):
        if isinstance(table._format,str):
            return table._format % record
        elif callable(table._format):
            return table._format(record)
        else:
            return '#'+str(record.id)

    if callable(field.represent):
        value = field.represent(value, row)
    else:
        referee = field.type[10:]
        if referee:
            record = db[referee]('id')
            value = format(db[referee], record)
    if not value:
        value = ''

    return value


def table_default_values(table):
    defaults = {}
    for fname in table.fields:
        if table[fname].default:
            if callable(table[fname].default):
                defaults[fname] = table[fname].default()
            else:
                defaults[fname] = table[fname].default
    return defaults


def _include_files(files):
    css_template = '<link href="%s" rel="stylesheet" type="text/css"/>' 
    js_template = '<script src="%s" type="text/javascript"></script>'

    hfiles = []
    for k in files:
        f = files[k]
        if f.endswith('.js'):
            hfiles.append(js_template % f)
        elif f.endswith('.css'):
            hfiles.append(css_template % f)

    return XML('\n'.join([f for f in hfiles]))  


def include_header_files():
    return _include_files(response.header_files)


def include_footer_files():
    return _include_files(response.footer_files)


def get_user_photo_url(user_id):
    url = URL('static','images/user-comment.png')
    if user_id == auth.user_id:
        if auth.user.photo:
            url = URL('default', 'download', args=auth.user.photo)
    elif db.auth_user[user_id].photo:
        url = URL('default', 'download', args=db.auth_user[user_id].photo)
    return url


