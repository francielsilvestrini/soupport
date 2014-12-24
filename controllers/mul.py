# -*- coding: utf-8 -*-

@auth.requires(lambda: auth_has_access())
def index():
    session.project = 'mul'

    query = (db.mul_contract_items > 0) & (db.mul_contract.id == db.mul_contract_items.contract_id)
    query &= (db.mul_contract_items.is_active == True) & (db.mul_contract.is_active == True)

    number = request.vars.get('contract')
    if number:
        query &= (db.mul_contract.number.like('%%%s%%' % number, case_sensitive=False) )


    ordened_rows = db(query).select(
        db.mul_contract_items.contract_id, db.mul_contract_items.id, 
        orderby=db.mul_contract_items.validate)

    keys = dict()
    rows = []
    for row in ordened_rows:
        if keys.get(row.contract_id):
            contract = keys[row.contract_id]
        else:
            contract = db(db.mul_contract.id == row.contract_id).select().first()
            ONXREPR.row_repr(contract, db.mul_contract)
            contract.items = []
            keys[row.contract_id] = contract
            rows.append(contract)

        item = db(db.mul_contract_items.id == row.id).select().first()
        ONXREPR.row_repr(item, db.mul_contract_items)
        contract.items.append(item)

    session.breadcrumbs.reset(T('MUL'), current_url())
    return dict(content=rows)


@auth.requires(lambda: auth_has_access())
def product():
    content = ONXFORM.make(db.mul_product)
    breadcrumbs_add()
    return content


@auth.requires(lambda: auth_has_access())
def contract():
    session.page.reset_files()

    def do_manager_extra_links(self, row):
        menu = [A(SPAN(T('Detail')), _href=URL(f='contract_detail', args=[row.id]))]
        return menu

    def do_grid_orderby(self):
        return ~db.mul_contract.number

    def do_navegate(self, nav, action):
        nav.next = current_url() if action == 'delete' else URL(f='contract_detail')+'/[id]'
        return nav

    def do_fields_list(self, action):
        fields=None
        if action in ['select']:
            hidden_fields = ['contract_date', 'note', 'contact', 'phone', 'email']
            fields = [f for f in db.mul_contract if f.readable and (not f.name in hidden_fields)]
        return fields

    def do_before_init(self, action):
        if action == 'new':
            max = db.mul_contract.number.max()
            number = db().select(max).first()[max]
            db.mul_contract.number.comment = 'Last contract number: %s' % number
        return

    oform = ONXFORM(db.mul_contract)
    oform.customize.on_manager_extra_links = do_manager_extra_links
    oform.customize.on_grid_orderby = do_grid_orderby
    oform.customize.on_navegate = do_navegate
    oform.customize.on_fields_list = do_fields_list
    oform.customize.on_before_init = do_before_init

    content = oform.get_current_action()

    breadcrumbs_add()    
    return content


@auth.requires(lambda: auth_has_access())
def contract_detail():
    session.page.reset_files()
    if not request.args(0) or not request.args[0].isdigit():
        raise HTTP(404, 'Invalid ID!')
    id = int(request.args[0])

    record = db(db.mul_contract.id == id).select().first()
    if not record:
        raise HTTP(404, 'Record not found!')

    ONXREPR.row_repr(record, db.mul_contract)

    response.title = T(db.mul_contract._singular)    
    response.subtitle = T('Detail')
    breadcrumbs_add(title=record.number)
    return dict(record=record)


def contract_items():
    try:
        contract_id = int(request.args(0))
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg=XML(T('Load method don\'t work!<br/> ERROR: %s') % str(e) ))

    rows = db(db.mul_contract_items.contract_id == contract_id).select()
    if rows:
        for row in rows:
            ONXREPR.row_repr(row, db.mul_contract_items)
    return dict(content=rows)


def contract_item():
    try:
        contract_id = int(request.args(0))
        item_id = None if request.args(1) == 'new' else int(request.args(1))
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg='contract items don\'t work!\nERROR: %s' % str(e) )

    db.mul_contract_items.contract_id.default = contract_id
    form = SQLFORM(db.mul_contract_items, item_id)
    if form.process().accepted:
        response.js = """
            $('#dialog_modal').modal('hide');
            web2py_component('%s','contract_items-load');
            """ % URL(f='contract_items.load', args=[contract_id])
    response.view = 'others/generic_modal.load'
    return dict(content=form)


def contract_item_remove():
    try:
        contract_id = int(request.args(0))
        item_id = int(request.args(1))
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg='contract items don\'t work!\nERROR: %s' % str(e) )

    db(db.mul_contract_items.id == item_id).delete()
    response.flash=T('Removed with success!')   
    response.js = 'web2py_component("%s","contract_items-load");' % URL(f='contract_items.load', args=[contract_id])
    return

def contract_item_renew():
    try:
        _id = str(request.vars.get('id'))
        args = _id.split('_')
        contract_id = args[1]
        item_id = args[2]
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg='contract items don\'t work!\nERROR: %s' % str(e) )

    query = (db.mul_contract_items.id == item_id)
    record = db(query).select().first()
    if record.validate < date.today():
        base_date = date.today()
    else:
        base_date = record.validate

    validate = base_date + timedelta(days=30)

    record.validate = validate
    record.licence_key = db.mul_contract_items.licence_key.compute(record)
    db(query).update(**record.as_dict())
    ONXREPR.row_repr(record, db.mul_contract_items)

    html = SPAN(record.repr.licence_key,
        **{'_title': '%s: %s' % (record.label.validate, record.repr.validate),
           '_data-toggle':'tooltip'})

    return XML(html)
