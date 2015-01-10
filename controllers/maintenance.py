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
                                    $("#maintenance_plan_item_notify_with").val(data.notify_with);
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
                                    $("#maintenance_control_item_notify_with").val(data.notify_with);
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
                _title=T('Current Life: {:.2f}%').format(percent),
                _class='bar',
                _style='width: {:.2f}%'.format(percent),
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

