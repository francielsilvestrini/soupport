# -*- coding: utf-8 -*-

@auth.requires(auth.has_membership(role=Settings.ADMIN_ROLE))
def index():
    session.project = 'painel'
    session.breadcrumbs.reset(T('Painel'), current_url())

    menus = []
    menus += [(T('Config'), URL(f='config'))]
    menus += [(T('Company'), URL(f='company'))]
    menus += [(T('Database'), URL(f='database'))]
    menus += [(T('Clear Cache'), URL(f='clear_cache'))]
    menus += [(T('Users'), URL(f='users'))]
    menus += [(T('Development'), URL(f='development'))]
    return dict(menus=menus)


@auth.requires(auth.has_membership(role=Settings.ADMIN_ROLE))
def config():
    def do_navegate(self, nav, action):
        nav.next = URL(c='painel', f='index')
        nav.previous = URL(c='painel', f='index')
        return

    record = PainelModel.config()

    oform = ONXFORM(db.painel)
    oform.save_and_add_enabled = False
    oform.customize.on_navegate = do_navegate
    content = oform.execute_action('update', record.id)

    response.breadcrumbs = T('Config')
    breadcrumbs_add()
    return content


@auth.requires(auth.has_membership(role=Settings.ADMIN_ROLE))
def company():
    def do_navegate(self, nav, action):
        nav.next = URL(c='painel', f='index')
        nav.previous = URL(c='painel', f='index')
        return

    record = PainelModel.company()

    oform = ONXFORM(db.company)
    oform.save_and_add_enabled = False
    oform.customize.on_navegate = do_navegate
    content = oform.execute_action('update', record.id)

    breadcrumbs_add()
    return content


@auth.requires(auth.has_membership(role=Settings.ADMIN_ROLE))
def database():
    menus = []
    menus += [(T('Backup'), URL(f='database_backup'))]
    menus += [(T('Clear'), URL(f='database_clear'))]
    menus += [(T('SQL Command'), URL(f='sql_command'))]
    response.breadcrumbs = T('Database')
    breadcrumbs_add()
    response.view = 'painel/index.html'
    return dict(menus=menus)


@auth.requires(auth.has_membership(role=Settings.ADMIN_ROLE))
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


@auth.requires(auth.has_membership(role=Settings.ADMIN_ROLE))
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


@auth.requires(auth.has_membership(role=Settings.ADMIN_ROLE))
def users():
    menus = []
    menus += [(T('Users'), URL(c='user', f='auth_user'))]
    menus += [(T('Users Group'), URL(c='user', f='auth_group'))]
    response.breadcrumbs = T('Users')
    breadcrumbs_add()
    response.view = 'painel/index.html'
    return dict(menus=menus)


@auth.requires(auth.has_membership(role=Settings.ADMIN_ROLE))
def development():
    menus = []
    menus += [(T('Translate'), URL(f='translate'))]
    menus += [(T('Log'), URL(f='log'))]
    response.breadcrumbs = T('Development')
    breadcrumbs_add()
    response.view = 'painel/index.html'
    return dict(menus=menus)


@auth.requires(auth.has_membership(role=Settings.ADMIN_ROLE))
def translate():
    response.breadcrumbs = T('Translate')
    breadcrumbs_add()

    fname1 = os.path.join(request.folder, 'languages','pt-br.py')
    fname2 = os.path.join(request.folder, 'languages','pt-br-1.py')
    fname_ig = os.path.join(request.folder, 'languages','pt-br.ignore')

    ins = open( fname1, "r" )
    ignore = []
    ins_ig = open( fname_ig, "r" )
    for s in ins_ig.readlines():
        ignore += [s]
    ins_ig.close()

    array = []
    separator = '\': \''
    for i, line in enumerate(ins.readlines()):
        if not separator in line:
            continue

        fields = line.split('\': \'')
        original = fields[0][1:]
        language = fields[1][0:-3]
        if '%s\n' % original in ignore:
            continue

        if len(original) > 2 and original == language:
            array.append( (i, original, language) )
    ins.close()

    rows = []
    for i, original, language in array:
        rows += [TR(
            DIV(
                P(original),
                DIV(A('>', _href='javascript:void(0);', _class='btn add-translate', **{'_data-id':i}), _class='pull-right')
            ),
            TEXTAREA(language, _name='key_%s'%i, _id='key_%s'%i),
            INPUT(_value=language, _name='original_%s'%i, _type='hidden'),
            INPUT(_name='ignore_%s'%i, _type='checkbox'),
            )]

    form = FORM(INPUT(_type='submit'), TABLE(rows, _class='table table-bordered'))
    if form.process().accepted:
        ins = open( fname1, "r" )
        ins_ig = open( fname_ig, "ab" )

        if os.path.exists(fname2):
            os.remove(fname2)
        new_file = open(fname2, "w")
        try:
            for i, line in enumerate(ins.readlines()):
                original = form.vars.get('original_%s'%i)
                language = form.vars.get('key_%s'%i)
                ignore = form.vars.get('ignore_%s'%i, '')

                if original != language:
                    line = '\'%s\': \'%s\',\n' % (original, language)
                new_file.write(line)
                if ignore == 'on':
                    ins_ig.write('%s\n' % original)
        finally:
            ins.close()
            new_file.close()
            ins_ig.close()
        if os.path.exists(fname1):
            os.remove(fname1)
        os.rename(fname2, fname1)
        redirect(URL(f='development'))

    response.title = T('Translate')
    response.subtitle = str(len(array))
    breadcrumbs_add(response.title)
    return dict(content=form)


@auth.requires(auth.has_membership(role=Settings.ADMIN_ROLE))
def log():
    if request.args(0) == 'clear':
        db(db.log.id > 0).delete()
        redirect(URL(f='log'))
        return

    content = ONXFORM.make(db.log)

    response.title = T('Log')
    response.subtitle = ''
    breadcrumbs_add(response.title)
    response.view = 'painel/log.html'
    return content


@auth.requires(auth.has_membership(role=Settings.ADMIN_ROLE))
def sql_command():
    command_type_set = {
        'command':T('Command'),
    }

    command = request.post_vars.get('command')
    command_type = request.post_vars.get('command_type', 'command')


    form = SQLFORM.factory(
            Field('command', 'text', label=T('Command'), default=command),
            Field('command_type', 'string', label=T('Command Type'), \
                requires=IS_IN_SET(command_type_set), default=command_type),
            )
    results = ''
    if form.process().accepted:
        command = form.vars['command']
        command_type = form.vars['command_type']
        if command_type == 'command':
            results = db.executesql(command)

    if not isinstance(results, (list,tuple)):
        results = [results]
    return dict(form=form, results=results)

