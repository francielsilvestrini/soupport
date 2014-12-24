# -*- coding: utf-8 -*-
 
query_my_tasks = (db.task.user_task == auth.user_id) & (db.task.status.belongs('analysis','development','test') )

query_waiting_tests = (db.task.status == 'test') 
query_waiting_tests &= (db.task.test_status.belongs('waiting', 'retest'))
query_waiting_tests &= (db.releases.id == db.task.test_release)

pagination = 10


def tasks_count(d):
    kSolicitations = db(db.solicitation.is_new == True).count()
    kTasks = db(query_my_tasks).count()
    kTests = db(query_waiting_tests).count()

    text = lambda k: {0: T('No Records'), 1: T('One Record'), 2: T('%s records') % k}[k if k < 2 else 2]

    d['kSolicitations'] = (kSolicitations, text(kSolicitations))
    d['kTasks'] = (kTasks, text(kTasks))
    d['kTests'] = (kTests, text(kTests))
    return


def make_search_form(opts, default_search):
    #opts = {'key': (description, query)}
    search_opts = []
    for k in opts:
        attr = {'_value':k}
        if k == request.vars.get('search_option', default_search):
            attr['_selected'] = 'selected'
        search_opts += [OPTION(opts[k][0], **attr)]

    wgt = []
    wgt += [SELECT(search_opts, _name='search_option')]
    wgt += [SPAN(' ')]
    wgt += [INPUT(_type='text', _name='search_text', _placeholder=T('Search'), _value=request.vars.get('search_text', ''))]
    wgt += [INPUT(_type='submit', _value=T('Search'))]
    return FORM(wgt, _method='get', _class='form-search')


def make_pagination(page, pages):
    wgt = []

    request.vars.page = page-1
    wgt += [LI(A('«', _href=URL(vars=request.vars)), _class='disabled' if page <= 1 else '')]

    for i in range(pages):
        request.vars.page = i+1
        wgt += [LI(A(i+1, _href=URL(vars=request.vars)), _class='active' if i+1 == page else 'inactive')]
    
    if not pages:
        wgt += [LI(A(T('No Records'), _href='#'), _class='active')]
        
    request.vars.page = page+1
    wgt += [LI(A('»', _href=URL(vars=request.vars)), _class='disabled' if page == pages else '')]
    return DIV(UL(wgt),_class='pagination pagination-right')


def pagination_calc(page, record_count):
    pagination = 10
    if page <= 0:
        page = 1

    pages = record_count/pagination
    if record_count%pagination:
        pages+=1

    if page > pages:
        page = pages

    limitby = (pagination*(page-1), (pagination*page))

    return (page, pages, limitby)


@auth.requires_login()
def index():
    session.project = 'tasks'
    session.breadcrumbs.reset(T('Tasks'), current_url())
    session.page.reset_files()
    search = dict(
        subject=(T('Subject'), lambda search: (db.solicitation.subject.like('%%%s%%' % search, case_sensitive=False)) ),
        customer=(T('Customer'), lambda search: (db.customer.name.like('%%%s%%' % search, case_sensitive=False)) ),
        content=(T('Content'), lambda search: (db.solicitation.content_txt.like('%%%s%%' % search, case_sensitive=False)) ),
        tag=(T('Tag'), lambda search: db.solicitation.tags.contains(search) ),
        )

    query = (db.solicitation.is_new == True)
    query &= (db.customer.id == db.solicitation.customer_id)
    search_text  = request.vars.get('search_text')
    if search_text:
        opt = request.vars.get('search_option', 'subject')
        opt_query = search[opt][1]
        query &= opt_query(search_text)

    try:
        page = int(request.vars.get('page', '1'))
    except:
        page = 1
    page, pages, limitby = pagination_calc(page=page, record_count=db(query).count())

    rows = db(query).select(
            limitby=limitby,
            orderby=~db.solicitation.id
            )

    content = dict(
        rows=rows,
        pagination=make_pagination(page, pages),
        search_form=make_search_form(search, 'subject'),
        )
    tasks_count(content)
    return content


@auth.requires_login()
def my_tasks():
    session.page.reset_files()
    search = dict(
        what=(T('What'), lambda search: (db.task.what.like('%%%s%%' % search, case_sensitive=False)) ),
        )

    query = query_my_tasks
    search_text  = request.vars.get('search_text')
    if search_text:
        opt = request.vars.get('search_option', 'what')
        opt_query = search[opt][1]
        query &= opt_query(search_text)

    try:
        page = int(request.vars.get('page', '1'))
    except:
        page = 1
    page, pages, limitby = pagination_calc(page=page, record_count=db(query).count())

    rows = db(query).select(
        limitby=limitby,
        orderby=(db.task.status, db.task.id))

    content = dict(
        rows=rows,
        pagination=make_pagination(page, pages),
        search_form=make_search_form(search, 'what'),
        )
    tasks_count(content)
    breadcrumbs_add(title=T('My Tasks'), reset=True)
    return content


@auth.requires_login()
def waiting_tests():
    session.page.reset_files()
    search = dict(
        what=(T('What'), lambda search: (db.task.what.like('%%%s%%' % search, case_sensitive=False)) ),
        test_release=(T('Test Release'), lambda search: (db.releases.name.like('%%%s%%' % search, case_sensitive=False)) ),
        )

    query = query_waiting_tests
    search_text  = request.vars.get('search_text')
    if search_text:
        opt = request.vars.get('search_option', 'what')
        opt_query = search[opt][1]
        query &= opt_query(search_text)

    try:
        page = int(request.vars.get('page', '1'))
    except:
        page = 1
    page, pages, limitby = pagination_calc(page=page, record_count=db(query).count())

    rows = db(query).select(
        limitby=limitby,
        orderby=(db.releases.name, db.task.id))

    content = dict(
        rows=rows,
        pagination=make_pagination(page, pages),
        search_form=make_search_form(search, 'what'),
        )
    tasks_count(content)
    breadcrumbs_add(title=T('Waiting Tests'), reset=True)
    return content


@auth.requires(lambda: auth_has_access())
def solicitation():
    session.page.reset_files()

    def do_manager_extra_links(self, row):
        menu = [A(SPAN(T('Detail')), _href=URL(f='solicitation_detail', args=[row.id]))]
        return menu

    def do_grid_orderby(self):
        return ~db.solicitation.id

    def do_form_success(form):
        tags = form.vars.get('tags', '')
        for name in tags.split(','):
            record = db(db.tag.name == name).select().first()
            if not record:
                db.tag.insert(name=name)        
        return

    def do_form_after_init(self, form, action):
        if action in ['new', 'update']:
            txt = form.elements('#solicitation_content_txt')
            if txt:
                txt[0] ['_class'] = 'span10'
        return

    def do_navegate(self, nav, action):
        nav.next = URL(f='index') if action == 'delete' else URL(f='solicitation_detail')+'/[id]'
        return nav

    oform = ONXFORM(db.solicitation)
    oform.customize.on_manager_extra_links = do_manager_extra_links
    oform.customize.on_grid_orderby = do_grid_orderby
    oform.customize.on_after_init = do_form_after_init
    oform.customize.on_navegate = do_navegate
    oform.customize.on_form_success = do_form_success

    content = oform.get_current_action()

    breadcrumbs_add()    
    return content


@auth.requires(lambda: auth_has_access())
def solicitation_detail():
    session.page.reset_files()
    if not request.args(0) or not request.args[0].isdigit():
        raise HTTP(404)
    id = int(request.args[0])

    record = db(db.solicitation.id == id).select().first()

    from h5_widgets import NicEditorWidget
    NicEditorWidget.widget_files()

    response.title = T(db.solicitation._plural)    
    response.subtitle = T('Detail')
    breadcrumbs_add(title=record.subject)
    return dict(record=record)


def solicitation_preview():
    record = None
    if request.vars.get('oplink'):
        oplink = request.vars.get('oplink')
        record = db(db.solicitation.oplink == oplink).select().first()
    elif request.vars.get('record_id'):
        id = int(request.vars.get('record_id'))
        record = db(db.solicitation.id == id).select().first()
    if not record:
        response.view = 'others/gadget_error.html'        
        return dict(msg='solicitation preview dont work!')

    return dict(record=record)


def _task_oform():

    def do_manager_extra_links(self, row):
        menu = [A(SPAN(T('Detail')), _href=URL(f='task_detail', args=[row.id])),
            A(SPAN(T('Flag as Released')), _href=URL(args=['flag_as_released', row.id]))]
        return menu

    def do_grid_orderby(self):
        return ~db.task.id

    def do_form_before_init(self, action):
        if action in ['new']:
            db.task.owner_table.default = 'task'
            db.task.owner_key.default = uuid.uuid4()
        return

    def do_form_after_init(self, form, action):
        if action in ['new', 'update']:
            txt = form.elements('#task_what')
            if txt:
                txt[0] ['_style'] = 'width:%s;'% '300px' if self.is_modal else '80%'
        return

    def do_fields_list(self, action):
        fields=None
        if action in ['new', 'update']:
            fields=['user_task', 'priority', 'status', 'what']
        elif action in ['select']:
            hidden_fields = ['user_task', 'priority', 'final_release']
            fields = [f for f in db.task if f.readable and (not f.name in hidden_fields)]
        return fields

    def do_navegate(self, nav, action):
        nav.next = URL(f='my_tasks') if action == 'delete' else URL(f='task_detail')+'/[id]'
        return nav

    oform = ONXFORM(db.task)
    oform.customize.on_manager_extra_links = do_manager_extra_links
    oform.customize.on_grid_orderby = do_grid_orderby
    oform.customize.on_before_init = do_form_before_init
    oform.customize.on_after_init = do_form_after_init
    oform.customize.on_navegate = do_navegate
    oform.customize.on_fields_list = do_fields_list

    return oform


@auth.requires(lambda: auth_has_access())
def task():
    session.page.reset_files()

    def action_flag_as_released():
        action = request.args(0) or ''
        if action == 'flag_as_released':
            next = session.breadcrumbs.last_url()
            try:
                id = int(request.args(1) or 0)
                record = db(db.task.id == id).select().first()
                if record:
                    record.update_record(final_release=record.test_release, status='released')
            except Exception, e:
                raise e
            finally:
                redirect(next)
        return

    #testa e executa a action, se executada será redirecionda
    action_flag_as_released()

    oform = _task_oform()
    content = oform.get_current_action()

    breadcrumbs_add()    
    return content


@auth.requires(lambda: auth_has_access())
def solicitation_to_task():
    owner_key = request.args(0) or ''
    solicitation = db(db.solicitation.oplink == owner_key).select().first()
    if not solicitation:
        raise HTTP(404)
    
    defaults = table_default_values(db.task)
    defaults['owner_table'] = 'solicitation'
    defaults['owner_key'] = owner_key
    defaults['what'] = solicitation.content_txt

    id = db.task.insert(**defaults)
    db(db.solicitation.oplink == owner_key).update(is_new=False)

    redirect(URL(f='task_detail', args=[id]))
    return


def tasks_list():
    owner_table = getlist(request.args, 0)
    owner_key  = getlist(request.args, 1)
    if not (owner_table and owner_key):
        response.view = 'others/gadget_error.html'        
        return dict(msg='tasks dont work!')

    query = ((db.task.owner_table == owner_table) & (db.task.owner_key == owner_key))
    
    tasks = db(query).select()
    return dict(tasks=tasks)


def tasks_modal_form():
    owner_table = request.args(0)
    owner_key  = request.args(1)
    if not (owner_table and owner_key):
        response.view = 'others/gadget_error.html'
        return dict(msg='task form dont work!')
    is_aceito = False

    def do_form_before_init(self, action):
        if action in ['new']:
            db.task.owner_table.default = owner_table
            db.task.owner_key.default = owner_key
        return

    def do_form_success(form):
        is_aceito = True
        if owner_table == 'solicitation':
            db(db.solicitation.oplink == owner_key).update(is_new=False)
        response.js = """
            $('#dialog_modal').modal('hide');
            web2py_component('%s','tasks_list');
            """ % URL(f='tasks_list.load', args=[owner_table, owner_key])
        return

    edit_id = request.vars.get('edit', 0)
        
    db.task.owner_table.default = owner_table
    db.task.owner_key.default = owner_key

    from gluon.storage import List
    _old_args = List(request.args)
    _old_vars = dict(request.vars)
    request.args = List()
    request.args.append('update' if edit_id > 0 else 'new')
    request.args.append(edit_id)

    oform = _task_oform()
    oform.customize.on_form_success = do_form_success
    oform.customize.on_before_init = do_form_before_init
    oform.is_modal = True
    oform.modal_cancel_onclick = "$('#dialog_modal').modal('hide');"

    content = oform.get_current_action()

    request.args = _old_args
    request.vars = _old_vars
    return content


@auth.requires(lambda: auth_has_access())
def task_detail():
    if not request.args(0) or not request.args[0].isdigit():
        raise HTTP(404)
    id = int(request.args[0])
    table = db.task

    record = db(db.task.id == id).select().first()

    has_test = db((db.test.owner_table == 'task') & (db.test.owner_key == record.oplink)).count()

    response.title = T(table._plural)    
    response.subtitle = T('Detail')

    from h5_widgets import NicEditorWidget
    NicEditorWidget.widget_files()

    breadcrumbs_add()    
    return dict(record=record,has_test=has_test)


def task_remove():
    owner_table = getlist(request.args, 0)
    owner_key  = getlist(request.args, 1)
    delete_id = request.vars.get('delete', 0)
    if delete_id:
        db(db.task.id == delete_id).delete()    
        response.js = "web2py_component('%s','tasks_list');" % URL(f='tasks_list.load', args=[owner_table, owner_key])
    pass


def task_detail_form():
    if not request.args(0) or not request.args[0].isdigit():
        raise HTTP(404)
    id = int(request.args[0])

    form = SQLFORM(db.task, id, fields=['note', 'status', 'final_release', 'test_status', 'test_release'])

    form.elements('#task_status')[0] ['_style'] = 'width:100%;'
    form.elements('#task_final_release')[0] ['_style'] = 'width:100%;'
    form.elements('#task_test_status')[0] ['_style'] = 'width:100%;'
    form.elements('#task_test_release')[0] ['_style'] = 'width:100%;'

    if form.process().accepted:
        response.js = 'window.location.reload(true);'

    return dict(form=form)


@auth.requires(lambda: auth_has_access())
def tests():
    if not request.args(0) or not request.args[0].isdigit():
        raise HTTP(404)
    id = int(request.args[0])
    table = db.task

    record = db(db.task.id == id).select().first()

    next_test = db((db.task.id > id) &
        (db.task.test_release == record.test_release) &
        query_waiting_tests).select(limitby=(0,1)).first()

    response.title = T('Tests')    
    response.subtitle = T('Task')

    db.test.owner_table.default = 'task'
    db.test.owner_key.default = record.oplink

    form = SQLFORM(db.test, fields=['note', 'test_result'])

    form.elements('#test_test_result')[0] ['_style'] = 'width:100%;'

    if form.process().accepted:
        record.update_record(test_status=form.vars.test_result)        
        next = form.vars.get('next')
        redirect(next or URL(f='index'))

    has_test = db((db.test.owner_table == 'task') & (db.test.owner_key == record.oplink)).count()

    if next_test:
        next_task = next_test.task
    else:
        next_task = None
    breadcrumbs_add()    
    return dict(record=record,next_test=next_task, form=form, has_test=has_test)


def tests_list():
    owner_table = getlist(request.args, 0)
    owner_key  = getlist(request.args, 1)
    if not (owner_table and owner_key):
        response.view = 'others/gadget_error.html'        
        return dict(msg='tests dont work!')

    query = ((db.test.owner_table == owner_table) & (db.test.owner_key == owner_key))
    
    tests = db(query).select()
    return dict(tests=tests)


@auth.requires(lambda: auth_has_access())
def release_history():
    orderby = (~db.releases.is_final | ~db.releases.id)
    releases = db(db.releases.id > 0).select(orderby=orderby)
    if not request.args(0) or not request.args[0].isdigit():
        try:
            release_id = releases[0].id
        except:
            release_id = 0
    else:
        release_id = int(request.args[0])    

    history = app_crud_grid((db.task.final_release == release_id),
        controller=request.controller, 
        function=request.function,
        **dict(show_link_edit=False, show_link_remove=False))
    response.title = T('Release History')    
    response.subtitle = T('Report')
    return dict(releases=releases, history=history)



@auth.requires(lambda: auth_has_access())
def test_history():
    orderby = (~db.releases.is_final | ~db.releases.id)
    releases = db(db.releases.id > 0).select(orderby=orderby)
    if not request.args(0) or not request.args[0].isdigit():
        release_id = releases[0].id
    else:
        release_id = int(request.args[0])    

    history = app_crud_grid((db.task.test_release == release_id),
        controller=request.controller, 
        function=request.function,
        **dict(show_link_edit=False, show_link_remove=False))
    response.title = T('Test History')    
    response.subtitle = T('Report')
    response.view = 'default/release_history.html'        
    return dict(releases=releases, history=history)


@auth.requires(lambda: auth_has_access())
def releases():
    content = ONXFORM.make(db.releases)
    breadcrumbs_add()
    return content
