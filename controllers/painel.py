# -*- coding: utf-8 -*-
from onx_views import ONXFORM 


@auth.requires(auth.has_membership(role=ADMIN_ROLE))
def index():
    session.project = 'painel'
    session.breadcrumbs.reset(T('Painel'), current_url())

    menus = []
    menus += [(T('Admin'), URL(f='admin'))]
    menus += [(T('Database'), URL(f='database'))]
    menus += [(T('Clear Cache'), URL(f='clear_cache'))]
    return dict(menus=menus)


@auth.requires(auth.has_membership(role=ADMIN_ROLE))
def admin():
    record = db(db.painel.id > 0).select().first()
    request.args.append('update')
    request.args.append(str(record.id))
    request.vars['_previous'] = URL(f='index')
    request.vars['_next'] = URL(f='index')
    content = ONXFORM.make(db.painel)
    breadcrumbs_add()    
    return content


@auth.requires(auth.has_membership(role=ADMIN_ROLE))
def database():
    menus = []
    menus += [(T('Backup'), URL(f='database_backup'))]
    menus += [(T('Clear'), URL(f='database_clear'))]
    response.breadcrumbs = T('Database')
    breadcrumbs_add()    
    response.view = 'painel/index.html'
    return dict(menus=menus)


@auth.requires(auth.has_membership(role=ADMIN_ROLE))
def database_backup():
    import cStringIO
    s = cStringIO.StringIO()
    db.export_to_csv_file(s)

    from gluon.contenttype import contenttype
    from datetime import datetime
    fname = 'backup %s.csv' % datetime.now().strftime("%d-%m-%y %H-%M-%S")
    response.headers['Content-Type'] = contenttype('.csv')
    response.headers['Content-disposition'] = 'attachment; ; filename=%s' % fname
    return s.getvalue()


@auth.requires(auth.has_membership(role=ADMIN_ROLE))
def database_clear():
    def make_form():
        tables = dict(all=T(' All '))
        for tname in db.tables:
            table = db[tname]
            tables[tname] = '%s (%s)' % (T(table._plural), db(table).count() )

        form = SQLFORM.factory(
            Field('table_name', 'string', label=T('Table Name'), requires = IS_IN_SET(tables, sort=True)),
            )
        return form

    form = make_form()
    if form.process().accepted:
        try:
            if form.vars.table_name == 'all':
                db.tables.reverse()
                for tname in db.tables:
                    db[tname].drop()
            else:
                db[form.vars.table_name].drop()
            form = make_form()
            response.flash = T('Successfully cleaned')
        except:
            response.flash = T('Error when cleaning')

    return dict(form=form)


def clear_cache():
    cache.ram.clear()
    cache.disk.clear()
    response.flash = T('Successfully cleaned')
    redirect(URL(f='index'))
    return




