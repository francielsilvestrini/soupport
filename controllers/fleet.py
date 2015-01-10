# -*- coding: utf-8 -*-

def _get_vehicle():
    vehicle_id = int( request.vars['vehicle'] )
    vehicle = db(db.vehicle.id == vehicle_id).select().first()
    ONXREPR.row_repr(vehicle, db.vehicle)
    return vehicle


@auth.requires(lambda: auth_has_access())
def index():
    session.project = 'fleet'
    session.breadcrumbs.reset(T('Fleet'), current_url())
    return dict()


@auth.requires(lambda: auth_has_access())
def vehicle_type():
    content = ONXFORM.make(db.vehicle_type)
    breadcrumbs_add()
    return content


@auth.requires(lambda: auth_has_access())
def vehicle():
    def do_fields_list(self, action):
        fields=[]
        if action in ['select']:
            for f in db.vehicle:
                if f.readable and getattr(f, 'show_grid', True):
                    fields += [f]
        elif action in ['read']:
            fields += ['licence_plate', 'description', 'current_odometer']
        return fields if len(fields) else None

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

    def do_before_init(self, action):
        if action == 'new':
            db.vehicle.accumulated_odometer.compute = lambda row: row.current_odometer
            db.vehicle.accumulated_odometer.writable = False
            db.vehicle.accumulated_odometer.readable = False
        return

    def do_form_success(form):
        id = int(form.vars.get('id', 0))
        if db(db.vehicle_status.vehicle_id == id).count() == 0:
            VehicleModel.vehicle_status_change(id, 'at_home', T('Begin control'))
        if db(db.vehicle_odometer.vehicle_id == id).count() == 0:
            VehicleModel.vehicle_odometer_change(
                vehicle_id=id,
                odometer_status='normal',
                odometer=float(form.vars['current_odometer']),
                note=T('Begin control'),
                owner_table='vehicle',
                owner_key=id,
                owner_link=URL(f='vehicle', args=['read', id])
                )
        return

    oform = ONXFORM(db.vehicle)
    oform.view_layout = 'fleet/vehicle.html'
    oform.customize.on_fields_list = do_fields_list
    oform.customize.on_form_success = do_form_success
    oform.customize.on_form_buttons = do_form_buttons
    oform.customize.on_navegate = do_navegate
    oform.customize.on_before_init = do_before_init
    oform.child_controls = True
    oform.save_and_add_enabled = False
    content = oform.get_current_action()

    children = [LOAD(c='fleet', f='vehicle_fuel.load', args=['list',request.args(1)], ajax=True, content=loading)]
    content['children'] = children

    breadcrumbs_add()
    return content


def vehicle_fuel():
    try:
        action = request.args(0)
        parent_id = int(request.args(1))
        item_id = int(request.args(2) or 0)
        table_item = db.vehicle_fuel
        target = request.function
        list_url = URL(f=target+'.load', args=['list', parent_id])

        def _do_get_content(*args):
            if action == 'list':
                rows = db(table_item.vehicle_id==parent_id).select()
                for row in rows:
                    ONXREPR.row_repr(row, table_item)
                return rows
            elif action == 'edit':
                response.view = 'others/generic_modal.load'
                table_item.vehicle_id.default = parent_id
                table_item.vehicle_id.writable = False
                form = SQLFORM(table_item, item_id, formstyle=formstyle_onx)
                return form

        content = ONXFORM.child_item(action, parent_id, item_id, table_item,
            target, list_url, _do_get_content)
        return content
    except Exception, e:
        response.view = 'others/load_error.html'
        return dict(msg=str(e) )


@auth.requires(lambda: auth_has_access())
def change_status():
    try:
        vehicle_id = int( request.vars['vehicle'] )
        status = str( request.args[0] )
        if not status in VehicleModel.vehicle_status.keys():
            raise Exception(T('Status not found!'))
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=T('ERROR: %s') % str(e) )

    VehicleModel.vehicle_status_change(vehicle_id, status, None)
    redirect(URL(f='dashboard', vars=request.vars))
    return


def add_status_note():
    try:
        status_id = int(request.args(0))
    except Exception, e:
        response.view = 'others/load_error.html'
        return dict(msg=T('ERROR: %s') % str(e) )

    db.vehicle_status.vehicle_id.writable=False
    db.vehicle_status.status.writable=False
    form = SQLFORM(db.vehicle_status, status_id, formstyle=formstyle_onx)
    if form.process().accepted:
        response.js = """
            window.location.reload(true);
            """
    response.view = 'others/generic_modal.load'
    return dict(content=form)


def toplinks():
    rows = db(db.vehicle.is_active == True).select(orderby=db.vehicle.licence_plate)
    if rows:
        for row in rows:
            ONXREPR.row_repr(row, db.vehicle)
            last_id = DBUTIL.last_id(db.vehicle_status, db.vehicle_status.vehicle_id == row.id)
            row_status = db(db.vehicle_status.id == last_id).select().first()
            ONXREPR.row_repr(row_status, db.vehicle_status)
            row_status.repr.color = VehicleModel.vehicle_status_color[row_status.status]
            row.status = row_status
    return dict(content=rows)


@auth.requires(lambda: auth_has_access())
def dashboard():
    try:
        vehicle_id = int( request.vars['vehicle'] )
        record = db(db.vehicle.id == vehicle_id).select().first()
        if not record:
            raise Exception(T('Record not found!'))
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=T('ERROR: %s') % str(e) )

    ONXREPR.row_repr(record, db.vehicle)

    control = db(db.maintenance_control.vehicle_id == record.id).select().first()
    record.maintenance_control_id = control.id if control else 0


    last_id = DBUTIL.last_id(db.vehicle_status, db.vehicle_status.vehicle_id == record.id)
    row_status = db(db.vehicle_status.id == last_id).select().first()
    ONXREPR.row_repr(row_status, db.vehicle_status)
    row_status.repr.color = VehicleModel.vehicle_status_color[row_status.status]
    record.status = row_status

    status_history = db(db.vehicle_status.vehicle_id==vehicle_id).select(orderby=~db.vehicle_status.id, limitby=(0,5))
    for row in status_history:
        ONXREPR.row_repr(row, db.vehicle_status)

    refueling = db(db.vehicle_refueling.vehicle_id==vehicle_id).select(
        orderby=~db.vehicle_refueling.id, limitby=(0,5))
    for row in refueling:
        ONXREPR.row_repr(row, db.vehicle_refueling)

    odometer = db(db.vehicle_odometer.vehicle_id == vehicle_id).select(orderby=~db.vehicle_odometer.id, limitby=(0,5))
    for row in odometer:
        ONXREPR.row_repr(row, db.vehicle_odometer)

    content = dict(
        record=record,
        status_list=VehicleModel.vehicle_status,
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
        vehicle = _get_vehicle()
        fuel = db(db.vehicle_fuel.vehicle_id == vehicle.id).select().first()
        if not fuel:
            raise Exception(T('Fuel not defined!'))
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=T('ERROR: %s') % str(e) )

    def do_navegate(self, nav, action):
        nav.next = URL(c='fleet', f='dashboard', vars=request.get_vars)
        nav.previous = URL(c='fleet', f='dashboard', vars=request.get_vars)
        return

    def do_grid_query(self):
        return (db.vehicle_refueling.vehicle_id == vehicle.id)


    def do_form_success(form):
        item_id = int(form.vars.get('id'))
        if db((db.vehicle_odometer.owner_table == 'vehicle_refueling')\
        & (db.vehicle_odometer.owner_key == str(item_id))).count() == 0:
            odometer = float(form.vars.get('current_odometer'))

            bus = VehicleModel.vehicle_odometer_change(
                vehicle_id=vehicle.id,
                odometer_status='normal',
                odometer=odometer,
                note=T('Refueling'),
                owner_table='vehicle_refueling',
                owner_key=item_id,
                owner_link=URL(vars=request.get_vars),
                )

            item = db.vehicle_refueling[item_id]
            current_refueling = bus['accumulated']
            distance = 0.0
            average = 0.0
            if item.old_refueling > 0.0:
                distance = current_refueling - item.old_refueling
                average = round(distance / item.liters, 3)

            item.update_record(
                current_refueling=current_refueling,
                distance=distance,
                average=average)
        return

    db.vehicle_refueling.vehicle_id.default = vehicle.id
    db.vehicle_refueling.vehicle_id.writable = False
    db.vehicle_refueling.fuel_id.requires = IS_IN_DB(
        db(db.vehicle_fuel.vehicle_id == vehicle.id),
        db.vehicle_fuel,
        db.vehicle_fuel._format)
    db.vehicle_refueling.fuel_id.default = fuel.id
    db.vehicle_refueling.current_odometer.comment = T('Vehicle Odometer: %s %s') % (vehicle.current_odometer, vehicle.repr.odometer_unit_id)
    db.vehicle_refueling.current_odometer.requires = IS_FLOAT_IN_RANGE(vehicle.current_odometer, None)

    db.vehicle_refueling.old_refueling.default = 0.0
    old_id = DBUTIL.last_id(db.vehicle_refueling, db.vehicle_refueling.vehicle_id == vehicle.id)
    if old_id:
        db.vehicle_refueling.old_refueling.default = db.vehicle_refueling[old_id].current_refueling

    oform = ONXFORM(db.vehicle_refueling)
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
        return (db.vehicle_odometer.vehicle_id == vehicle_id)

    db.vehicle_odometer.vehicle_id.default = vehicle_id
    db.vehicle_odometer.vehicle_id.writable = False

    oform = ONXFORM(db.vehicle_odometer)
    oform.customize.on_navegate = do_navegate
    oform.customize.on_grid_query = do_grid_query

    content = oform.get_current_action()
    breadcrumbs_add()
    return content


@auth.requires(lambda: auth_has_access())
def reset_odometer():
    try:
        vehicle = _get_vehicle()
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=T('ERROR: %s') % str(e) )

    def do_form_success(form):
        odometer = float(form.vars['odometer'])
        VehicleModel.vehicle_odometer_change(
            vehicle_id=vehicle.id,
            odometer_status='normal',
            odometer=odometer,
            note=form.vars['note'],
            owner_table=None,
            owner_key=None,
            owner_link=None,
            )
        VehicleModel.vehicle_odometer_change(
            vehicle_id=vehicle.id,
            odometer_status='odometer_reset',
            odometer=0.00,
            note=T('Restarted'),
            owner_table=None,
            owner_key=None,
            owner_link=None,
            )
        Maintenance.odometer_reseted(vehicle.id, odometer)
        return

    db.vehicle_odometer.vehicle_id.default = vehicle.id
    db.vehicle_odometer.vehicle_id.writable = False
    db.vehicle_odometer.odometer.comment = T('Vehicle Odometer: %s %s') % (vehicle.current_odometer, vehicle.repr.odometer_unit_id)
    db.vehicle_odometer.odometer.requires = IS_FLOAT_IN_RANGE(vehicle.current_odometer, None)

    form = SQLFORM.factory(
        db.vehicle_odometer.vehicle_id,
        db.vehicle_odometer.odometer,
        db.vehicle_odometer.note,
        formstyle=formstyle_onx,
        _class='form-horizontal onx-form')
    if form.process(onsuccess=do_form_success).accepted:
        redirect( URL(c='fleet', f='dashboard', vars=request.get_vars) )

    response.view = 'others/generic_crud.html'
    response.title = T('Reset Odometer')
    breadcrumbs_add(response.title)
    return dict(content=form)
