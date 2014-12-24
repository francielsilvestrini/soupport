# -*- coding: utf-8 -*-

@auth.requires(lambda: auth_has_access())
def index():
    session.project = 'fleet'
    session.breadcrumbs.reset(T('Fleet'), current_url())
    return dict()


@auth.requires(lambda: auth_has_access())
def inventory_item():
    content = ONXFORM.make(db.O1_inventory_item)
    breadcrumbs_add()
    return content


@auth.requires(lambda: auth_has_access())
def vehicle_type():
    content = ONXFORM.make(db.O2_vehicle_type)
    breadcrumbs_add()
    return content


@auth.requires(lambda: auth_has_access())
def vehicle():
    def do_fields_list(self, action):
        fields=[]
        if action in ['select']:
            for f in db.O2_vehicle:
                if f.readable and getattr(f, 'show_grid', True):
                    fields += [f]
        elif action in ['read']:
            fields += ['licence_plate', 'description', 'odometer']
        return fields if len(fields) else None

    def do_form_success(form):
        id = int(form.vars.get('id', 0))
        if db(db.O2_vehicle_status.vehicle_id == id).count() == 0:
            defs = table_default_values(db.O2_vehicle_status)
            defs['vehicle_id'] = id
            defs['status'] = 'at_home'
            db.O2_vehicle_status.insert(**defs)
        return

    def do_form_buttons(self, action, buttons):
        btns = buttons
        if action == 'read':
            _id = request.args(1) or 0
            _vars = request.vars.copy()
            _vars['redirect'] = session.breadcrumbs.last_url()
            btns = [
                A(T('Edit'), _class='btn btn-primary', _href=URL(c='fleet', f='vehicle', args=['update', _id], vars=_vars)),
                SPAN(' '),
                A(T('Cancel'), _class='btn', _href=_vars['redirect']),
                ]                
        return btns

    def do_navegate(self, nav, action):
        if action == 'new':
            nav.next = URL(c='fleet', f='vehicle', args=['read', '[id]'], url_encode=False)
        return

    oform = ONXFORM(db.O2_vehicle)
    oform.view_layout = 'fleet/vehicle.html'
    oform.customize.on_fields_list = do_fields_list
    oform.customize.on_form_success = do_form_success
    oform.customize.on_form_buttons = do_form_buttons
    oform.customize.on_navegate = do_navegate
    oform.child_controls = True
    oform.save_and_add_enabled = False
    content = oform.get_current_action()
    breadcrumbs_add()
    return content


def vehicle_fuel():
    try:
        parent_id = int(request.args(0))
    except Exception, e:
        response.view = 'others/load_error.html'        
        return dict(msg=T('ERROR: %s') % str(e) )

    rows = db(db.O2_vehicle_fuel.vehicle_id==parent_id).select()
    for row in rows:
        ONXREPR.row_repr(row, db.O2_vehicle_fuel)    
    return dict(content=rows)       


def vehicle_fuel_edit():
    try:
        parent_id = int(request.args(0))
        item_id = int(request.args(1))
    except Exception, e:
        response.view = 'others/load_error.html'        
        return dict(msg=T('ERROR: %s') % str(e) )

    db.O2_vehicle_fuel.vehicle_id.default = parent_id
    db.O2_vehicle_fuel.vehicle_id.writable = False
    form = SQLFORM(db.O2_vehicle_fuel, item_id)
    if form.process().accepted:
        response.js = """
            $('#dialog_modal').modal('hide');
            web2py_component('%s','vehicle_fuel-load');
            """ % URL(f='vehicle_fuel.load', args=[parent_id])
    response.view = 'others/generic_modal.load'
    return dict(content=form)       


def vehicle_fuel_remove():
    try:
        parent_id = int(request.args(0))
        item_id = int(request.args(1))
    except Exception, e:
        response.view = 'others/load_error.html'        
        return dict(msg=T('ERROR: %s') % str(e) )

    db(db.O2_vehicle_fuel.id == item_id).delete()
    response.flash=T('Removed with success!')   
    response.js = """
        web2py_component('%s','vehicle_fuel-load');
        """ % URL(f='vehicle_fuel.load', args=[parent_id])
    return


@auth.requires(lambda: auth_has_access())
def change_status():
    try:
        vehicle_id = int( request.vars['vehicle'] )
        status = str( request.args[0] )
        if not status in O2Model.vehicle_status.keys():
            raise Exception(T('Status not found!'))
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg=T('ERROR: %s') % str(e) )

    defs = table_default_values(db.O2_vehicle_status)
    defs['vehicle_id'] = vehicle_id
    defs['status'] = status
    db.O2_vehicle_status.insert(**defs)
    redirect(URL(f='dashboard', vars=request.vars))
    return


def add_status_note():
    try:
        status_id = int(request.args(0))
    except Exception, e:
        response.view = 'others/load_error.html'        
        return dict(msg=T('ERROR: %s') % str(e) )

    db.O2_vehicle_status.vehicle_id.writable=False
    db.O2_vehicle_status.status.writable=False
    form = SQLFORM(db.O2_vehicle_status, status_id)
    if form.process().accepted:
        response.js = """
            window.location.reload(true);
            """
    response.view = 'others/generic_modal.load'
    return dict(content=form)    


def toplinks():
    rows = db(db.O2_vehicle.is_active == True).select(orderby=db.O2_vehicle.licence_plate)
    if rows:
        for row in rows:
            ONXREPR.row_repr(row, db.O2_vehicle)
            last_id = DBUTIL.last_id(db.O2_vehicle_status, db.O2_vehicle_status.vehicle_id == row.id)
            row_status = db(db.O2_vehicle_status.id == last_id).select().first()
            ONXREPR.row_repr(row_status, db.O2_vehicle_status)
            row_status.repr.color = O2Model.vehicle_status_color[row_status.status]
            row.status = row_status
    return dict(content=rows)


@auth.requires(lambda: auth_has_access())
def dashboard():
    try:
        vehicle_id = int( request.vars['vehicle'] )
        record = db(db.O2_vehicle.id == vehicle_id).select().first()
        if not record:
            raise Exception(T('Record not found!'))
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg=T('ERROR: %s') % str(e) )

    ONXREPR.row_repr(record, db.O2_vehicle)

    last_id = DBUTIL.last_id(db.O2_vehicle_status, db.O2_vehicle_status.vehicle_id == record.id)
    row_status = db(db.O2_vehicle_status.id == last_id).select().first()
    ONXREPR.row_repr(row_status, db.O2_vehicle_status)
    row_status.repr.color = O2Model.vehicle_status_color[row_status.status]
    record.status = row_status

    status_history = db(db.O2_vehicle_status.vehicle_id==vehicle_id).select(orderby=~db.O2_vehicle_status.id, limitby=(0,5))
    for row in status_history:
        ONXREPR.row_repr(row, db.O2_vehicle_status)    

    refueling = db(db.O2_vehicle_refueling.vehicle_id==vehicle_id).select(
        orderby=~db.O2_vehicle_refueling.id, limitby=(0,5))
    for row in refueling:
        ONXREPR.row_repr(row, db.O2_vehicle_refueling)

    odometer = db(db.O2_vehicle_odometer.vehicle_id == vehicle_id).select(orderby=~db.O2_vehicle_odometer.id, limitby=(0,5))
    for row in odometer:
        ONXREPR.row_repr(row, db.O2_vehicle_odometer)

    content = dict(
        record=record,
        status_list=O2Model.vehicle_status,
        status_history=status_history,
        refueling=refueling,
        odometer=odometer,)

    session.breadcrumbs.reset(T('Fleet'), URL(c='fleet',f='index'))
    response.title = T('Dashboard')
    response.subtitle = T(record.repr.licence_plate)
    response.breadcrumbs = response.title
    breadcrumbs_add()
    return content


@auth.requires(lambda: auth_has_access())
def refueling():
    try:
        vehicle_id = int( request.vars['vehicle'] )
        fuel = db(db.O2_vehicle_fuel.vehicle_id == vehicle_id).select().first()
        if not fuel:
            raise Exception(T('Fuel not defined!'))
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg=T('ERROR: %s') % str(e) )

    def do_form_success(form):
        item_id = int(form.vars.get('id'))
        odometer = float(form.vars.get('odometer'))
        status = form.vars.get('odometer_status')

        O2Model.odometer_change(
            'O2_vehicle_refueling', item_id, vehicle_id, odometer, 
            status, T('Refueling'))
        return

    def do_navegate(self, nav, action):
        nav.next = URL(c='fleet', f='dashboard', vars=request.get_vars)
        nav.previous = URL(c='fleet', f='dashboard', vars=request.get_vars)
        return

    def do_grid_query(self):
        return (db.O2_vehicle_refueling.vehicle_id == vehicle_id)

    old_id = DBUTIL.last_id(db.O2_vehicle_refueling, db.O2_vehicle_fuel.vehicle_id == vehicle_id)
    old_refueling = db(db.O2_vehicle_refueling.id == old_id).select().first()

    db.O2_vehicle_refueling.vehicle_id.default = vehicle_id
    db.O2_vehicle_refueling.vehicle_id.writable = False
    db.O2_vehicle_refueling.fuel_id.requires = IS_IN_DB(
        db(db.O2_vehicle_fuel.vehicle_id == vehicle_id), 
        db.O2_vehicle_fuel, 
        db.O2_vehicle_fuel._format)
    db.O2_vehicle_refueling.fuel_id.default = fuel.id
    if old_refueling:
        db.O2_vehicle_refueling.old_odometer.default = old_refueling.odometer
    else:
        vehicle = db(db.O2_vehicle.id == vehicle_id).select().first()
        db.O2_vehicle_refueling.old_odometer.default = vehicle.odometer
    db.O2_vehicle_refueling.old_odometer.writable = False

    oform = ONXFORM(db.O2_vehicle_refueling)
    oform.view_layout = 'fleet/refueling.html'
    oform.customize.on_form_success = do_form_success
    oform.customize.on_navegate = do_navegate
    oform.customize.on_grid_query = do_grid_query

    content = oform.get_current_action()
    breadcrumbs_add()
    return content


@auth.requires(lambda: auth_has_access())
def odometer():
    try:
        vehicle_id = int( request.vars['vehicle'] )
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg=T('ERROR: %s') % str(e) )

    def do_navegate(self, nav, action):
        nav.next = URL(c='fleet', f='dashboard', vars=request.get_vars)
        nav.previous = URL(c='fleet', f='dashboard', vars=request.get_vars)
        return

    def do_grid_query(self):
        return (db.O2_vehicle_odometer.vehicle_id == vehicle_id)

    db.O2_vehicle_odometer.vehicle_id.default = vehicle_id
    db.O2_vehicle_odometer.vehicle_id.writable = False

    oform = ONXFORM(db.O2_vehicle_odometer)
    oform.customize.on_navegate = do_navegate
    oform.customize.on_grid_query = do_grid_query

    content = oform.get_current_action()
    breadcrumbs_add()
    return content    