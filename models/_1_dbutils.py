# -*- coding: utf-8 -*-


UPLOAD_URLS = {
    'profile': path.join(request.folder,'uploads','profile'),
    'attachments': path.join(request.folder,'uploads','attachments'),
}


def table_default_values(table):
    from onx_utils import OnxUtils
    defaults = OnxUtils.table_default_values(table)
    return defaults


def get_user_photo_url(user_id):
    url = URL('static','images/user-comment.png')
    if user_id == auth.user_id:
        if auth.user.photo:
            url = URL('default', 'download', args=auth.user.photo)
    elif db.auth_user[user_id].photo:
        url = URL('default', 'download', args=db.auth_user[user_id].photo)
    return url


###############################################################################
# REPRESENTATION METHODS
###############################################################################

def field_rep(field, value, row):
    ''' remover
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
    '''
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

class ONXREPR(object):

    @staticmethod
    def row_repr(row, table):
        row.repr = Storage()
        row.label = Storage()
        for f in table:
            row.repr[f.name] = field_rep(f, row[f.name], row)
            row.label[f.name] = f.label
        return

    @staticmethod
    def repr_yes_no(value, row):
        return T('Yes' if value else 'No')

    @staticmethod
    def repr_updated_on_pretty(value, row):
        pretty_date = prettydate(value, T)
        return T('Updated %s') % pretty_date

    @staticmethod
    def repr_updated_by(value, row):
        author_name = '%(first_name)s %(last_name)s' % db.auth_user[value]
        return T(' by %s') % author_name

    @staticmethod
    def repr_text(value, row):
        txt = XML(value.replace('\n', '<br />'), sanitize=True, permitted_tags=['br/'])
        return txt

    @staticmethod
    def repr_mailto(value, row):
        return XML(A(value, _href='mailto:%s'%value))


###############################################################################

class DBUTIL(object):

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

###############################################################################

