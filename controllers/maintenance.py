# -*- coding: utf-8 -*-

def crud(table):
    content = ONXFORM.make(table)
    breadcrumbs_add()
    return content


@auth.requires(lambda: auth_has_access())
def maintenance_service():
    if request.extension == 'json':
        service_id = int(request.vars.get('id'))
        record = db.maintenance_service[service_id].as_dict()
        return response.json(record)

    return crud(db.maintenance_service)


@auth.requires(lambda: auth_has_access())
def maintenance_plan():
    oform = ONXFORM(db.maintenance_plan)
    oform.view_layout = 'others/form_children.html'
    oform.child_controls = True
    oform.save_and_add_enabled = False
    content = oform.get_current_action()
    breadcrumbs_add()

    children = [LOAD(f='maintenance_plan_item.load', args=['list',request.args(1)], ajax=True, content=loading)]
    content['children'] = children
    return content


def maintenance_plan_item():
    try:
        action = request.args(0)
        parent_id = int(request.args(1))
        item_id = int(request.args(2) or 0)
        table_item = db.maintenance_plan_item
        target = request.function
        list_url = URL(f=target+'.load', args=['list', parent_id])

        def _do_get_content(*args):
            if action == 'list':
                rows = db(table_item.plan_id==parent_id).select()
                for row in rows:
                    ONXREPR.row_repr(row, table_item)
                return rows
            elif action == 'edit':
                response.view = 'others/generic_modal.load'
                table_item.plan_id.default = parent_id
                table_item.plan_id.writable = False
                form = SQLFORM(table_item, item_id, formstyle=formstyle_onx)
                js = '''
                    $(document).ready (function () {
                        $("#maintenance_plan_item_service_id").change(function() {
                            var service_id = $(this).val();
                            $.ajax({
                                url: "%(url)s",
                                data: {id:service_id},
                                cache: false,
                                success: function(data){
                                    $("#maintenance_plan_item_maintenance_interval").val(data.maintenance_interval);
                                }
                            });
                        });
                    });
                    ''' % dict(url=URL(f='maintenance_service.json'))
                form[0].append(SCRIPT(js, _type="text/javascript"))

                return form

        content = ONXFORM.child_item(action, parent_id, item_id, table_item,
            target, list_url, _do_get_content)
        return content
    except Exception, e:
        response.view = 'others/load_error.html'
        return dict(msg=str(e) )


def _get_vehicle(vehicle_id=None):
    if not vehicle_id:
        vehicle_id = int( request.vars['vehicle'] )
    vehicle = db(db.vehicle.id == vehicle_id).select().first()
    ONXREPR.row_repr(vehicle, db.vehicle)
    return vehicle


@auth.requires(lambda: auth_has_access())
def create():
    try:
        vehicle = _get_vehicle()
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=str(e) )

    def do_form_success(form):
        control_id = int(form.vars['id'])
        plan_id = int(form.vars['plan_id'])
        MaintenanceModel.change_plan(control_id, plan_id, vehicle.current_odometer)
        return

    db.maintenance_control.vehicle_id.default = vehicle.id

    oform = ONXFORM(db.maintenance_control)
    oform.save_and_add_enabled = False
    oform.customize.on_form_success = do_form_success
    content = oform.execute_action('new', 0)

    response.page_alerts.append((
        T('Warning!'),
        T('Last maintenance equal the current vehicle odometer! Edit to change.'),
        'warning'))

    response.title = T('Create Maintenance')
    response.subtitle = ''
    breadcrumbs_add()
    return content


@auth.requires(lambda: auth_has_access())
def manage():
    try:
        vehicle = _get_vehicle()
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=str(e) )

    bc = session.breadcrumbs
    control = db(db.maintenance_control.vehicle_id == vehicle.id).select().first()

    if not control:
        new_vars = clear_vars_navegate(request.get_vars)
        new_vars['next'] = current_url()
        new_vars['previous'] = bc.last_url()
        redirect(URL(f='create', vars=new_vars))

    children = [LOAD(f='maintenance_control_item.load', args=['list',control.id], ajax=True, content=loading)]

    bc_parts = bc.last_url_parts()
    if bc_parts['function'] == 'create':
        bc.delete_current()
    response.title = T('Maintenance')
    breadcrumbs_add(response.title)
    content = dict(
        content='',
        vehicle=vehicle,
        children=children)
    return content


def maintenance_control_item():
    try:
        action = request.args(0)
        parent_id = int(request.args(1))
        item_id = int(request.args(2) or 0)
        table_item = db.maintenance_control_item
        target = request.function
        list_url = URL(f=target+'.load', args=['list', parent_id])

        def _do_get_content(*args):
            if action == 'list':
                rows = db(table_item.control_id==parent_id).select()
                for row in rows:
                    ONXREPR.row_repr(row, table_item)
                return rows
            elif action == 'edit':
                response.view = 'others/generic_modal.load'

                control = db(db.maintenance_control.id == parent_id).select().first()
                vehicle = _get_vehicle(control.vehicle_id)
                table_item.control_id.default = control.id
                table_item.control_id.writable = False
                table_item.vehicle_id.default = control.vehicle_id
                table_item.vehicle_id.writable = False
                table_item.last_maintenance.comment = T('Vehicle Odometer: %s %s') % (vehicle.current_odometer, vehicle.repr.odometer_unit_id)

                form = SQLFORM(table_item, item_id, formstyle=formstyle_onx)

                js = '''
                    $(document).ready (function () {
                        function change_interval() {
                            var interval = parseFloat($("#maintenance_control_item_maintenance_interval").val());
                            var last = parseFloat($("#maintenance_control_item_last_maintenance").val());
                            $("#maintenance_control_item_next_maintenance").val(interval+last);
                        }


                        $("#maintenance_control_item_maintenance_interval").change(function() {
                            change_interval();
                        });
                        $("#maintenance_control_item_last_maintenance").change(function() {
                            change_interval();
                        });
                        $("#maintenance_control_item_service_id").change(function() {
                            var service_id = $(this).val();
                            $.ajax({
                                url: "%(url)s",
                                data: {id:service_id},
                                cache: false,
                                success: function(data){
                                    $("#maintenance_control_item_maintenance_interval").val(data.maintenance_interval);
                                }
                            });
                        });
                    });
                    ''' % dict(url=URL(f='maintenance_service.json'))
                form[0].append(SCRIPT(js, _type="text/javascript"))
                return form


        content = ONXFORM.child_item(action, parent_id, item_id, table_item,
            target, list_url, _do_get_content)
        return content
    except Exception, e:
        response.view = 'others/load_error.html'
        return dict(msg=str(e) )


def maintenance():
    def _get_progress_bar(percent):
        if percent >= 95.00:
            _class = 'progress-danger'
        elif percent >= 85.00:
            _class = 'progress-warning'
        elif percent >= 70.00:
            _class = 'progress-info'
        else:
            _class = 'progress-success'
        bar = DIV(
            DIV(
                _title=T('Current Life: {0:.2f}%').format(percent),
                _class='bar',
                _style='width: {0:.2f}%'.format(percent),
                **{'_data-toggle':'tooltip'}
                ),
            _class='progress %s' % _class)
        return bar

    try:
        action = request.args(0)
        parent_id = int(request.args(1))
        item_id = int(request.args(2) or 0)
        table_item = db.maintenance_control_item

        if action == 'list':
            rows = db(table_item.control_id==parent_id).select(orderby=db.maintenance_control_item.next_maintenance)
            vehicle = None
            for row in rows:
                ONXREPR.row_repr(row, table_item)
                if not vehicle:
                    vehicle = _get_vehicle(row.vehicle_id)
                percent = 100.0
                diference = row.next_maintenance - vehicle.current_odometer
                if diference > 0.0:
                    percent = 100.0 - round((diference * 100)/row.maintenance_interval, 2)

                row.repr.percent = percent
                row.repr.bar = _get_progress_bar(percent)
            return dict(content=rows)


        return dict()
    except Exception, e:
        response.view = 'others/load_error.html'
        return dict(msg=str(e) )


@auth.requires(lambda: auth_has_access())
def order():
    try:
        vehicle = _get_vehicle()
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=str(e) )

    def do_navegate(self, nav, action):
        nav.previous = URL(c='fleet', f='dashboard', vars=request.get_vars)
        return

    def do_grid_query(self):
        if vehicle:
            query = (db.maintenance_order.vehicle_id == vehicle.id)
        else:
            query = (db.maintenance_order.vehicle_id > 0)
        return query

    def do_before_init(self, action):
        db.maintenance_order.vehicle_id.default = vehicle.id
        db.maintenance_order.vehicle_id.writable = False
        if action in ['new', 'update']:
            db.maintenance_order.current_odometer.comment = T('Vehicle Odometer: %s %s') % (vehicle.current_odometer, vehicle.repr.odometer_unit_id)
        if action in ['new', 'update', 'read']:
            for fname in ['services', 'materials', 'discount', 'total_order','status']:
                db.maintenance_order[fname].readable = False
                db.maintenance_order[fname].writable = False
        return

    oform = ONXFORM(db.maintenance_order)
    oform.customize.on_navegate = do_navegate
    oform.customize.on_grid_query = do_grid_query
    oform.customize.on_before_init = do_before_init
    oform.view_layout = 'others/form_children.html'
    oform.child_controls = True
    oform.save_and_add_enabled = False

    content = oform.get_current_action()

    children = [
        LOAD(f='maintenance_order_services.load', args=['list',request.args(1)], vars=request.get_vars, ajax=True, content=loading),
        LOAD(f='maintenance_order_materials.load', args=['list',request.args(1)], vars=request.get_vars, ajax=True, content=loading),
        LOAD(f='maintenance_order_status.load', args=['list',request.args(1)], vars=request.get_vars, ajax=True, content=loading),
        ]
    content['children'] = children

    breadcrumbs_add()
    return content


def maintenance_order_services():
    try:
        action = request.args(0)
        parent_id = int(request.args(1))
        item_id = int(request.args(2) or 0)
        table_item = db.maintenance_order_services
        target = request.function
        list_url = URL(f=target+'.load', args=['list', parent_id])

        def _do_get_content(*args):
            if action == 'list':
                rows = db(table_item.order_id==parent_id).select()
                for row in rows:
                    ONXREPR.row_repr(row, table_item)
                return rows
            elif action == 'edit':
                response.view = 'others/generic_modal.load'

                parent = db(db.maintenance_order.id == parent_id).select().first()
                vehicle = _get_vehicle(parent.vehicle_id)
                table_item.order_id.default = parent.id
                table_item.order_id.writable = False
                table_item.next_maintenance.comment = T('Order Odometer: %s %s') % (parent.current_odometer, vehicle.repr.odometer_unit_id)
                table_item.service_id.default = request.vars.get('service')

                js_change_service = '$("#maintenance_order_services_service_id").trigger("change");' if table_item.service_id.default else ''

                form = SQLFORM(table_item, item_id, formstyle=formstyle_onx_modal)
                js = '''
                    $(document).ready (function () {
                        function change_interval() {
                            var interval = parseFloat($("#maintenance_order_services_maintenance_interval").val());
                            if (interval > 0) {
                                $("#maintenance_order_services_next_maintenance").val(interval+%(current_odometer)s);
                            }
                        }

                        $("#maintenance_order_services_maintenance_interval").change(function() {
                            change_interval();
                        });

                        $("#maintenance_order_services_service_id").change(function() {
                            var service_id = $(this).val();
                            $.ajax({
                                url: "%(url)s",
                                data: {id:service_id},
                                cache: false,
                                success: function(data){
                                    $("#maintenance_order_services_maintenance_interval").val(data.maintenance_interval);
                                    change_interval();
                                }
                            });
                        });
                        %(js_change_service)s
                    });
                    ''' % dict(url=URL(f='maintenance_service.json'), current_odometer=parent.current_odometer, js_change_service=js_change_service)
                form[0].append(SCRIPT(js, _type="text/javascript"))
                content = dict(
                    form=form,
                    extra_js="web2py_component('%s','%s-load');" % (
                        URL(f='maintenance_order_status.load', args=['list',parent_id], vars=request.get_vars),
                        'maintenance_order_status')
                    )
                return content

        def do_success_form(form):
            sum_field = DBUTIL.sum_field(db.maintenance_order_services.cost, (db.maintenance_order_services.order_id == parent_id))
            parent = db(db.maintenance_order.id == parent_id).select().first()
            parent.update_record(services=sum_field, total_order=sum_field+parent.materials-parent.discount)

            return
        content = ONXFORM.child_item(action, parent_id, item_id, table_item,
            target, list_url, _do_get_content, onsuccess=do_success_form)
        return content
    except Exception, e:
        response.view = 'others/load_error.html'
        return dict(msg=str(e) )


def maintenance_order_materials():
    try:
        action = request.args(0)
        parent_id = int(request.args(1))
        item_id = int(request.args(2) or 0)
        table_item = db.maintenance_order_materials
        target = request.function
        list_url = URL(f=target+'.load', args=['list', parent_id])

        def _do_get_content(*args):
            if action == 'list':
                rows = db(table_item.order_id==parent_id).select()
                for row in rows:
                    ONXREPR.row_repr(row, table_item)
                return rows
            elif action == 'edit':
                response.view = 'others/generic_modal.load'

                parent = db(db.maintenance_order.id == parent_id).select().first()
                vehicle = _get_vehicle(parent.vehicle_id)
                table_item.order_id.default = parent.id
                table_item.service_reference_id.requires = IS_EMPTY_OR(
                    IS_IN_DB(db(db.maintenance_order_services.order_id == parent_id), db.maintenance_order_services, db.maintenance_order_services._format)
                    )

                form = SQLFORM(table_item, item_id, formstyle=formstyle_onx_modal)
                js = '''
                    $(document).ready (function () {
                        function update_total() {
                            var quantity = parseFloat($("#maintenance_order_materials_quantity").val());
                            var unit_cost = parseFloat($("#maintenance_order_materials_unit_cost").val());
                            var discount = parseFloat($("#maintenance_order_materials_discount").val());

                            $("#maintenance_order_materials_total_cost").val((quantity*unit_cost)-discount);
                        }

                        $("#maintenance_order_materials_quantity,"
                         +" #maintenance_order_materials_unit_cost,"
                         +" #maintenance_order_materials_discount").change(function() {
                            update_total();
                        });

                        $("#maintenance_order_materials_add_to_stock_add").click(function() {
                            var quantity = parseFloat($("#maintenance_order_materials_quantity").val());
                            $("#maintenance_order_materials_add_to_stock").val(quantity);
                        });

                        $("#maintenance_order_materials_add_to_order_add").click(function() {
                            var total = parseFloat($("#maintenance_order_materials_total_cost").val());
                            $("#maintenance_order_materials_add_to_order").val(total);
                        });
                    });
                    ''' % dict(url=URL(f='maintenance_service.json'), current_odometer=parent.current_odometer)
                form[0].append(SCRIPT(js, _type="text/javascript"))

                btn_attr = {
                    '_href':'javascript:void(0);',
                    '_class':'btn btn-small btn-info',
                    '_style':'height: 24px;margin-right: 3px;',
                    '_data-toggle':'tooltip',
                }

                btn_attr['_title'] = T('Quantity to add in stock')
                btn_attr['_id'] = 'maintenance_order_materials_add_to_stock_add'
                btn_add = A(I(_class='fa fa-hand-o-right'), **btn_attr)
                div_controls = form[0].elements('#maintenance_order_materials_add_to_stock__row .controls')[0]
                div_controls.insert(0, DIV(btn_add, _class='pull-left'))

                btn_attr['_title'] = T('Sum to order cost')
                btn_attr['_id'] = 'maintenance_order_materials_add_to_order_add'
                btn_add = A(I(_class='fa fa-hand-o-right'), **btn_attr)
                div_controls = form[0].elements('#maintenance_order_materials_add_to_order__row .controls')[0]
                div_controls.insert(0, DIV(btn_add, _class='pull-left'))

                content = dict(
                    form=form,
                    extra_js="web2py_component('%s','%s-load');" % (
                        URL(f='maintenance_order_status.load', args=['list',parent_id], vars=request.get_vars),
                        'maintenance_order_status')
                    )
                return content

        def do_success_form(form):
            sum_field = DBUTIL.sum_field(db.maintenance_order_materials.add_to_order, (db.maintenance_order_materials.order_id == parent_id))
            parent = db(db.maintenance_order.id == parent_id).select().first()
            parent.update_record(materials=sum_field, total_order=parent.services+sum_field-parent.discount)
            return

        content = ONXFORM.child_item(action, parent_id, item_id, table_item,
            target, list_url, _do_get_content, onsuccess=do_success_form)
        return content
    except Exception, e:
        response.view = 'others/load_error.html'
        return dict(msg=str(e) )


def maintenance_order_status():

    try:
        action = request.args(0)
        parent_id = int(request.args(1))

        fields = ['status','services', 'materials','discount','total_order',]
        parent = db(db.maintenance_order.id == parent_id).select().first()
        old_status = parent.status
        if old_status == 'finalized':
            db.maintenance_order.status.writable = False

        form = SQLFORM(db.maintenance_order,
            parent_id,
            fields=fields,
            submit_button=T('Save'),
            showid=False,
            formstyle=formstyle_onx)
        if form.process(formname='maintenance_order_status_form').accepted:
            parent = db(db.maintenance_order.id == parent_id).select().first()
            if old_status != 'finalized' and parent.status == 'finalized':
                #update odometer
                VehicleModel.vehicle_odometer_change(
                    vehicle_id=parent.vehicle_id,
                    odometer_status='normal',
                    odometer=parent.current_odometer,
                    note=T('Order Maintenance')+' #'+str(parent.id),
                    owner_table='maintenance_order',
                    owner_key=parent_id,
                    owner_link=URL(f='order', args=['read', parent_id], vars=request.get_vars))

                for service in db(db.maintenance_order_services.order_id == parent_id).select():
                    if service.next_maintenance > 0.0:
                        MaintenanceModel.update_maintenance(
                            vehicle_id=parent.vehicle_id,
                            service_id=service.service_id,
                            last_maintenance=parent.current_odometer,
                            maintenance_interval=service.maintenance_interval,
                            next_maintenance=service.next_maintenance)

            if parent.status == 'finalized':
                response.js = 'window.location.assign("%s");' % URL(c='fleet', f='dashboard.html', vars=request.get_vars, host=True)

        return dict(form=form)
    except Exception, e:
        response.view = 'others/load_error.html'
        return dict(msg=str(e) )