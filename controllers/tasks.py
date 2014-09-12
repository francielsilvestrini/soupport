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
    return content


@auth.requires_login()
def waiting_tests():
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
    return content


def _get_crud_id():
    if not request.args(1) or not request.args[1].isdigit():
        raise HTTP(404)
    return int(request.args[1])


def app_crud(table, **attr):
    action = request.args(0) or ''
    if not action in ('new','edit', 'remove', 'delete'):
        raise HTTP(404)

    if action == 'new':
        response.subtitle = T('New Record')
        content = crud.create(table, **attr)
    else:
        id = _get_crud_id()

        if isinstance(table._format,str):
            registro = table._format % table[id]
        else:
            registro = table._format(table[id])

        if action == 'remove':
            response.subtitle = T('Confirm delete "')+ registro +'" ?'
            content = crud.read(table, id)
        elif action == 'delete':
            crud.delete(table, id, **attr)
        else:
            response.subtitle = T('Editing: ')+ registro
            content = crud.update(table, id, deletable=False, **attr)
    response.title = T(table._plural)    
    return content


from gluon.dal import Table
def app_crud_grid(table, controller=request.controller, function=request.function, **attr):
    exportclasses = dict(
        csv_with_hidden_cols=False,
        json=False,
        tsv_with_hidden_cols=False,
        tsv=False
    )

    links = []
    extra_links = attr.get('extra_links', [])
    links += [link for link in extra_links]

    if attr.get('show_link_edit', True):
        caption = '' if len(extra_links) else ' '+T('Edit')
        links += [lambda row: A(
            SPAN(_class="icon pen icon-pencil")+ caption,
            _href=URL(c=controller, f=function, args=['edit', row.id]), 
            _class="w2p_trap button btn btn-small")]

    if attr.get('show_link_remove', True):
        links += [lambda row: A(
            SPAN(_class="icon icon-trash"),
            _href=URL(c=controller, f=function, args=['remove', row.id]), 
            _class="w2p_trap button btn btn-small")]

    local_attr = dict(
        user_signature=False,
        exportclasses=exportclasses,
        deletable=False,
        editable=False,
        details=False,
        create=False,
        links=links,
        args=[],
        paginate=25,
        maxtextlength=50,
        #maxtextlengths=maxtextlengths,      
        #field_id=None,
        #left=None,
        #headers={},
        #orderby=None,
        #groupby=None,
        #searchable=True,
        #sortable=True,
        #selectable=None,
        #csv=True,
        #links_in_grid=True,
        #upload='<default>',
        #onvalidation=None,
        #oncreate=None,
        #onupdate=None,
        #ondelete=None,
        #sorter_icons=(XML('&#x2191;'), XML('&#x2193;')),
        #ui = 'web2py',
        #showbuttontext=True,
        #_class="web2py_grid",
        #formname='web2py_grid',
        #search_widget='default',
        #ignore_rw = False,
        #formstyle = 'table3cols',
        #formargs={},
        #createargs={},
        #editargs={},
        #viewargs={},
        #buttons_placement = 'right',
        #links_placement = 'right'
        )
    local_attr.update(attr)

    for kname in ['extra_links', 'show_link_edit', 'show_link_remove']:
        if local_attr.has_key(kname):
            del local_attr[kname]

    grid = SQLFORM.grid(table, **local_attr)
    if isinstance(table, Table):
        response.title = T(table._plural)    
        response.subtitle = T('Listing')
    return grid


def solicitation_accept(form):
    tags = form.vars.get('tags', '')
    for name in tags.split(','):
        record = db(db.tag.name == name).select().first()
        if not record:
            db.tag.insert(name=name)        
    return


@auth.requires_login()
def solicitation():
    action = request.args(0) or ''

    if action == '':
        extra_links =  [lambda row: A(
            SPAN(_class="icon icon-eye-open")+' '+T('Detail'),
            _href=URL(f='solicitation_detail', args=[row.id]), 
            _class="w2p_trap button btn btn-small")]
        content = app_crud_grid(db.solicitation, 
            controller=request.controller, 
            function=request.function,
            **dict(extra_links=extra_links, orderby=~db.solicitation.id) )
    else:
        attr = dict(
            next=URL(f='index') if action == 'delete' else URL(f='solicitation_detail')+'/[id]',
            )

        if action == 'new':
            content = crud.create(db.solicitation, onaccept=lambda form:solicitation_accept(form), **attr)
            response.title = T(db.solicitation._plural)    
            response.subtitle = T('New Record')
        else:
            if action == 'edit':
                row = db(db.solicitation.id == _get_crud_id()).select().first()
                attr['onaccept'] = lambda form:solicitation_accept(form)
            content = app_crud(db.solicitation, **attr)

        if action in ('new', 'edit'):
            my_extra_element = nic_editor_js('solicitation_content_txt')
            content[0].insert(-1, my_extra_element)

    return dict(content=content)


@auth.requires_login()
def solicitation_detail():
    if not request.args(0) or not request.args[0].isdigit():
        raise HTTP(404)
    id = int(request.args[0])

    record = db(db.solicitation.id == id).select().first()

    response.title = T(db.solicitation._plural)    
    response.subtitle = T('Detail')
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


@auth.requires_login()
def customer():
    response.view = 'others/generic_crud.html'
    action = request.args(0) or ''

    if action == '':
        content = app_crud_grid(db.customer, controller=request.controller, function=request.function)
    else:
        content = app_crud(db.customer)
    return dict(content=content)


@auth.requires_login()
def releases():
    response.view = 'others/generic_crud.html'
    action = request.args(0) or ''

    if action == '':
        content = app_crud_grid(db.releases, controller=request.controller, function=request.function)
    else:
        content = app_crud(db.releases)
    return dict(content=content)


@auth.requires_login()
def task():
    action = request.args(0) or ''

    if action == '':
        extra_links =  [lambda row: A(
            SPAN(_class="icon icon-eye-open")+' '+T('Detail'),
            _href=URL(f='task_detail', args=[row.id]), 
            _class="w2p_trap button btn btn-small")]
        content = app_crud_grid(db.task, 
            controller=request.controller, 
            function=request.function,
            **dict(extra_links=extra_links,orderby=~db.task.id) )
    else:
        attr = dict(
            next=URL(f='index') if action == 'delete' else URL(f='task_detail')+'/[id]',
            fields=['user_task', 'priority', 'status', 'what'],
            )
        if request.vars.get('next'):
            attr['next'] = request.vars['next']
        
        if action == 'delete':
            del attr['fields']
        elif action == 'new':#spare task
            db.task.owner_table.default = 'task'
            db.task.owner_key.default = uuid.uuid4()

        content = app_crud(db.task, **attr)
        if action in ('new', 'edit'):
            my_extra_element = nic_editor_js('task_what')
            content[0].insert(-1, my_extra_element)
        if action == 'edit':
            response.subtitle = T('Editing...')
    return dict(content=content)


@auth.requires_login()
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
    owner_table = getlist(request.args, 0)
    owner_key  = getlist(request.args, 1)
    if not (owner_table and owner_key):
        response.view = 'others/gadget_error.html'        
        return dict(msg='task form dont work!')

    edit_id = request.vars.get('edit', 0)
        
    db.task.owner_table.default = owner_table
    db.task.owner_key.default = owner_key

    form = SQLFORM(db.task, edit_id, fields=['user_task', 'priority', 'status', 'what'])

    my_extra_element = nic_editor_js('task_what', '500px')
    form[0].insert(-1, my_extra_element)

    if form.process().accepted:
        if owner_table == 'solicitation':
            db(db.solicitation.oplink == owner_key).update(is_new=False)
        response.js = "$('#dialog_modal').modal('hide'); web2py_component('%s','tasks_list');" % URL(f='tasks_list.load', args=[owner_table, owner_key])

    return dict(form=form)


@auth.requires_login()
def task_detail():
    if not request.args(0) or not request.args[0].isdigit():
        raise HTTP(404)
    id = int(request.args[0])
    table = db.task

    record = db(db.task.id == id).select().first()

    has_test = db((db.test.owner_table == 'task') & (db.test.owner_key == record.oplink)).count()

    response.title = T(table._plural)    
    response.subtitle = T('Detail')
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

    my_extra_element = DIV( nic_editor_js('task_note', '100%'), _id='task_detail_form_nic')
    form[0].insert(-1, my_extra_element)

    form.elements('#task_status')[0] ['_style'] = 'width:100%;'
    form.elements('#task_final_release')[0] ['_style'] = 'width:100%;'
    form.elements('#task_test_status')[0] ['_style'] = 'width:100%;'
    form.elements('#task_test_release')[0] ['_style'] = 'width:100%;'

    if form.process().accepted:
        response.js = 'window.location.reload(true);'

    return dict(form=form)


@auth.requires_login()
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

    my_extra_element = DIV( nic_editor_js('test_note', '100%'), _id='test_form_nic')
    form[0].insert(-1, my_extra_element)
    form.elements('#test_test_result')[0] ['_style'] = 'width:100%;'

    if form.process().accepted:
        record.update_record(test_status=form.vars.test_result)        
        next = form.vars.get('next')
        redirect(next or URL(f='index'))

    has_test = db((db.test.owner_table == 'task') & (db.test.owner_key == record.oplink)).count()

    return dict(record=record,next_test=next_test.task, form=form, has_test=has_test)


def tests_list():
    owner_table = getlist(request.args, 0)
    owner_key  = getlist(request.args, 1)
    if not (owner_table and owner_key):
        response.view = 'others/gadget_error.html'        
        return dict(msg='tests dont work!')

    query = ((db.test.owner_table == owner_table) & (db.test.owner_key == owner_key))
    
    tests = db(query).select()
    return dict(tests=tests)


@auth.requires_login()
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



@auth.requires_login()
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
