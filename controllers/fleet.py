# -*- coding: utf-8 -*-

def _get_vehicle(vehicle_id=None):
    if not vehicle_id:
        vehicle_id = int( request.vars['vehicle'] )
    vehicle = db(db.vehicle.id == vehicle_id).select().first()
    ONXREPR.row_repr(vehicle, db.vehicle)
    return vehicle


def one_month_ago():
    return request.now.today() - timedelta(days=30)


def one_year_ago():
    return request.now.today() - timedelta(days=365)


def _distance_traveled(vehicle_id):
    def odometer_history(vid, initial_date):
        row = db((db.vehicle_odometer.vehicle_id==vid) & (db.vehicle_odometer.odometer_date >= initial_date)).select(
            orderby=db.vehicle_odometer.odometer_date, limitby=(0,1)).first()
        return row

    data = {}
    if vehicle_id != None:
        query = (db.vehicle.id == vehicle_id)
    else:
        query = (db.vehicle.is_active == True)
    for vehicle in db(query).select():
        data_item = {}
        data_item['licence_plate'] = vehicle.licence_plate
        data_item['description'] = vehicle.description
        data_item['month'] = ('0km', 0.0)
        data_item['year'] = ('0km', 0.0)

        history = odometer_history(vehicle.id, one_month_ago())
        if history:
            value = round(vehicle.accumulated_odometer - history.accumulated, 3)
            data_item['month'] = ('%skm' % value, value)
        history = odometer_history(vehicle.id, one_year_ago())
        if history:
            value = round(vehicle.accumulated_odometer - history.accumulated, 3)
            data_item['year'] = ('%skm' % value, value)
        data[vehicle.id] = data_item
    return data


def _fleet_summary():
    data = {
        'vehicle_count': {
            'text' :A(T('Vehicle Count'), _href=URL(c='fleet', f='vehicle')),
            'month':('', 0),
            'year' :('', 0),
            },
        'distance_traveled': {
            'text' :A(T('Distance Traveled'), _href=URL(c='fleet', f='distance_traveled')),
            'month':('0km', 0.0),
            'year' :('0km', 0.0),
            },
        'distance_traveled_by_vehicle': {
            'text' :A(T('Distance Traveled by Vehicle'), _href=URL(c='fleet', f='distance_traveled')),
            'month':('0km', 0.0),
            'year' :('0km', 0.0),
            },
        'fuel_cost': {
            'text' :T('Fuel Cost'),
            'month':('$0.00', 0.0),
            'year' :('$0.00', 0.0),
            },
        'fuel_cost_by_vehicle': {
            'text' :T('Fuel Cost by Vehicle'),
            'month':('$0.00', 0.0),
            'year' :('$0.00', 0.0),
            },
        'maintenance_order': {
            'text' :T('Maintenance Order'),
            'month':('$0.00', 0.0),
            'year' :('$0.00', 0.0),
            },
        'maintenance_order_by_vehicle': {
            'text' :T('Maintenance Order by Vehicle'),
            'month':('$0.00', 0.0),
            'year' :('$0.00', 0.0),
            },
    }

    # vehicle_count
    data_item = data['vehicle_count']
    vehicle_count = db(db.vehicle.is_active == True).count()
    data_item['month'] = (str(vehicle_count), vehicle_count)

    # distance_traveled
    data_item = data['distance_traveled']
    distance_all_vehicles = _distance_traveled(None)
    month, year = 0.0, 0.0
    for vid in distance_all_vehicles:
        vehicle = distance_all_vehicles[vid]
        month += vehicle['month'][1]
        year += vehicle['year'][1]
    data_item['month'] = ('%skm' % month, month)
    data_item['year'] = ('%skm' % year, year)

    # distance_traveled_by_vehicle
    if vehicle_count > 0:
        data_item = data['distance_traveled_by_vehicle']
        value = round(month/vehicle_count, 3)
        data_item['month'] = ('%skm' % value, value)
        value = round(year/vehicle_count, 3)
        data_item['year'] = ('%skm' % value, value)

    # fuel cost
    data_item = data['fuel_cost']
    value = DBUTIL.sum_field(db.vehicle_refueling.total_price, (db.vehicle_refueling.refueling_date >= one_month_ago()))
    value = round(value or 0.0, 2)
    data_item['month'] = ('$%.2f' % value, value)

    value = DBUTIL.sum_field(db.vehicle_refueling.total_price, (db.vehicle_refueling.refueling_date >= one_year_ago()))
    value = round(value or 0.0, 2)
    data_item['year'] = ('$%.2f' % value, value)

    # fuel_cost_by_vehicle
    if vehicle_count > 0:
        data_item = data['fuel_cost_by_vehicle']
        month = data['fuel_cost']['month'][1]
        value = round(month/vehicle_count, 2)
        data_item['month'] = ('$%.2f' % value, value)
        year = data['fuel_cost']['year'][1]
        value = round(year/vehicle_count, 2)
        data_item['year'] = ('$%.2f' % value, value)

    # maintenance_order
    data_item = data['maintenance_order']
    value = DBUTIL.sum_field(db.maintenance_order.total_order,
        (db.maintenance_order.status == 'finalized') & (db.maintenance_order.order_date >= one_month_ago()))
    value = round(value or 0.0, 2)
    data_item['month'] = ('$%.2f' % value, value)

    value = DBUTIL.sum_field(db.maintenance_order.total_order,
        (db.maintenance_order.status == 'finalized') & (db.maintenance_order.order_date >= one_year_ago()))
    value = round(value or 0.0, 2)
    data_item['year'] = ('$%.2f' % value, value)

    # maintenance_order_by_vehicle
    if vehicle_count > 0:
        data_item = data['maintenance_order_by_vehicle']
        month = data['maintenance_order']['month'][1]
        value = round(month/vehicle_count, 2)
        data_item['month'] = ('$%.2f' % value, value)
        year = data['maintenance_order']['year'][1]
        value = round(year/vehicle_count, 2)
        data_item['year'] = ('$%.2f' % value, value)

    return data


@auth.requires(lambda: auth_has_access())
def index():
    session.project = 'fleet'
    session.breadcrumbs.reset(T('Fleet'), current_url())


    content = dict(
        summary=_fleet_summary(),
        )
    return content


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


def _maintenance_order(vehicle_id):
    maintenance_order = db((db.maintenance_order.vehicle_id==vehicle_id) & (db.maintenance_order.status == 'open')).select(
        orderby=db.maintenance_order.id, limitby=(0,5))
    for row in maintenance_order:
        ONXREPR.row_repr(row, db.maintenance_order)

    group_month = db.maintenance_order.order_date.year()|db.maintenance_order.order_date.month()
    sum = db.maintenance_order.total_order.sum()
    statistics = db((db.maintenance_order.vehicle_id==vehicle_id) & (db.maintenance_order.status == 'finalized')).select(
        db.maintenance_order.order_date, sum, groupby=group_month, limitby=(0,5))
    return Dict(open=maintenance_order, statistics=statistics)


def _vehicle_summary(vehicle_id):
    data = {
        'distance_traveled': {
            'item' :T('Distance Traveled'),
            'month':('0km', 0.0),
            'year' :('0km', 0.0),
        },
        'fuel_cost': {
            'item' :T('Fuel Cost'),
            'month':('$0.00', 0.0),
            'year' :('$0.00', 0.0),
        },
        'fuel_liters': {
            'item' :T('Fuel Liters'),
            'month':('0lt', 0.0),
            'year' :('0lt', 0.0),
        },
        'fuel_average': {
            'item' :T('Fuel Average'),
            'month':('0km/lt', 0.0),
            'year' :('0km/lt', 0.0),
        },
        'maintenance_order': {
            'item' :T('Maintenance Order'),
            'month':('$0.00', 0.0),
            'year' :('$0.00', 0.0),
        },

    }

    vehicle = _get_vehicle(vehicle_id)

    # distance traveled
    data_item = data['distance_traveled']
    history = _distance_traveled(vehicle.id)
    data_item['month'] = history[vehicle.id]['month']
    data_item['year'] = history[vehicle.id]['year']

    # fuel cost
    data_item = data['fuel_cost']
    value = DBUTIL.sum_field(db.vehicle_refueling.total_price,
        (db.vehicle_refueling.vehicle_id==vehicle_id) & (db.vehicle_refueling.refueling_date >= one_month_ago()))
    value = round(value or 0.0, 2)
    data_item['month'] = ('$%s' % value, value)

    value = DBUTIL.sum_field(db.vehicle_refueling.total_price,
        (db.vehicle_refueling.vehicle_id==vehicle_id) & (db.vehicle_refueling.refueling_date >= one_year_ago()))
    value = round(value or 0.0, 2)
    data_item['year'] = ('$%s' % value, value)

    # fuel liters
    data_item = data['fuel_liters']
    value = DBUTIL.sum_field(db.vehicle_refueling.liters,
        (db.vehicle_refueling.vehicle_id==vehicle_id) & (db.vehicle_refueling.refueling_date >= one_month_ago()))
    value = round(value or 0.0, 3)
    data_item['month'] = ('%slt' % value, value)

    value = DBUTIL.sum_field(db.vehicle_refueling.liters,
        (db.vehicle_refueling.vehicle_id==vehicle_id) & (db.vehicle_refueling.refueling_date >= one_year_ago()))
    value = round(value or 0.0, 3)
    data_item['year'] = ('%slt' % value, value)

    # fuel average
    data_item = data['fuel_average']
    distance = data['distance_traveled']['month'][1]
    liters = data['fuel_liters']['month'][1]
    if liters > 0.0:
        value = round(distance/liters, 3)
    else:
        value = 0.0
    data_item['month'] = ('%skm/lt' % value, value)

    distance = data['distance_traveled']['year'][1]
    liters = data['fuel_liters']['year'][1]
    if liters > 0.0:
        value = round(distance/liters, 3)
    else:
        value = 0.0
    data_item['year'] = ('%skm/lt' % value, value)

    # maintenance order
    data_item = data['maintenance_order']
    value = DBUTIL.sum_field(db.maintenance_order.total_order,
        (db.maintenance_order.vehicle_id==vehicle_id) \
        & (db.maintenance_order.status == 'finalized') \
        & (db.maintenance_order.order_date >= one_month_ago()))
    value = round(value or 0.0, 2)
    data_item['month'] = ('$%s' % value, value)

    data_item = data['maintenance_order']
    value = DBUTIL.sum_field(db.maintenance_order.total_order,
        (db.maintenance_order.vehicle_id==vehicle_id) \
        & (db.maintenance_order.status == 'finalized') \
        & (db.maintenance_order.order_date >= one_year_ago()))
    value = round(value or 0.0, 2)
    data_item['year'] = ('$%s' % value, value)
    return data


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
        odometer=odometer,
        maintenance_order=_maintenance_order(vehicle_id),
        summary=_vehicle_summary(vehicle_id),
        )

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


@auth.requires(lambda: auth_has_access())
def distance_traveled():
    data = _distance_traveled(None)
    response.title = T('Distance Traveled')
    breadcrumbs_add()
    return dict(data=data)
