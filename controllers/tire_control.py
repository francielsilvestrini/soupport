# -*- coding: utf-8 -*-

img_style = 'width: 100%;height: 100%;'

tc_items_order = db.tire_control_item.axle_position \
    | db.tire_control_item.axle_sequence \
    | db.tire_control_item.wheel_side \
    | db.tire_control_item.wheel_position


def _static_url(filename):
    url = URL('static', filename, host=True)
    return url


def _get_chassi_table(design):
    td_style = 'width: 40px;height: 90px;padding: 0px;'

    table_rows = []
    part = design.get('front', {})
    axle_part = ('P1', 'P2', 'P3')
    for sequence in part:
        left = part[sequence].get('left', {})
        right = part[sequence].get('right', {})
        table_rows += [TR(
            TD(left.get(4, ''), _style=td_style),
            TD(left.get(3, ''), _style=td_style),
            TD(left.get(2, ''), _style=td_style),
            TD(left.get(1, ''), _style=td_style),
            TD(IMG(_style=img_style, _src=_static_url('images/tire_control/chassi/%s.png'%axle_part[0])), _style=td_style),
            TD(IMG(_style=img_style, _src=_static_url('images/tire_control/chassi/%s.png'%axle_part[1])), _style=td_style),
            TD(IMG(_style=img_style, _src=_static_url('images/tire_control/chassi/%s.png'%axle_part[2])), _style=td_style),
            TD(right.get(1, ''), _style=td_style),
            TD(right.get(2, ''), _style=td_style),
            TD(right.get(3, ''), _style=td_style),
            TD(right.get(4, ''), _style=td_style),
            )]
        axle_part = ('P13', 'P14', 'P15')

    table_rows += [TR(
        TD('', _style=td_style),
        TD('', _style=td_style),
        TD('', _style=td_style),
        TD('', _style=td_style),
        TD(IMG(_style=img_style,_src=_static_url('images/tire_control/chassi/P4.png')), _style=td_style),
        TD(IMG(_style=img_style,_src=_static_url('images/tire_control/chassi/P5.png')), _style=td_style),
        TD(IMG(_style=img_style,_src=_static_url('images/tire_control/chassi/P6.png')), _style=td_style),
        TD('', _style=td_style),
        TD('', _style=td_style),
        TD('', _style=td_style),
        TD('', _style=td_style),
        )]

    part = design.get('rear', {})
    axle_part = ('P7', 'P8', 'P9')
    for sequence in part:
        left = part[sequence].get('left', {})
        right = part[sequence].get('right', {})
        table_rows += [TR(
            TD(left.get(4, ''), _style=td_style),
            TD(left.get(3, ''), _style=td_style),
            TD(left.get(2, ''), _style=td_style),
            TD(left.get(1, ''), _style=td_style),
            TD(IMG(_style=img_style,_src=_static_url('images/tire_control/chassi/%s.png'%axle_part[0])), _style=td_style),
            TD(IMG(_style=img_style,_src=_static_url('images/tire_control/chassi/%s.png'%axle_part[1])), _style=td_style),
            TD(IMG(_style=img_style,_src=_static_url('images/tire_control/chassi/%s.png'%axle_part[2])), _style=td_style),
            TD(right.get(1, ''), _style=td_style),
            TD(right.get(2, ''), _style=td_style),
            TD(right.get(3, ''), _style=td_style),
            TD(right.get(4, ''), _style=td_style),
            )]
        axle_part = ('P10', 'P11', 'P12')

    part = design.get('steppe', {})
    for sequence in part:
        left = part[sequence].get('left', {})
        right = part[sequence].get('right', {})
        table_rows += [TR(
            TD('', _style=td_style),
            TD(left.get(4, ''), _style=td_style),
            TD(left.get(3, ''), _style=td_style),
            TD(left.get(2, ''), _style=td_style),
            TD(left.get(1, ''), _style=td_style),
            TD('', _style=td_style),
            TD(right.get(1, ''), _style=td_style),
            TD(right.get(2, ''), _style=td_style),
            TD(right.get(3, ''), _style=td_style),
            TD(right.get(4, ''), _style=td_style),
            TD('', _style=td_style),
            )]
    return TABLE(TBODY(table_rows), _style='width: 440px;border-spacing: 0px;')


def _get_chassi_design(tc_id, item_selected, is_manage):
    tc_items = db(db.tire_control_item.tire_control_id == tc_id).select(orderby=tc_items_order)

    design = dict()
    new_vars = clear_vars_navegate(request.get_vars)

    wheels = {
        'left': {
            'in': ('left_in', 'left_in_sel'),
            'out': ('left_out', 'left_out_sel'),
        },
        'right': {
            'in': ('right_in', 'right_in_sel'),
            'out': ('right_out', 'right_out_sel'),
        },
        'steppe': {
            'in': ('steppe_in', 'steppe_in_sel'),
            'out': ('steppe_out', 'steppe_out_sel'),
        },
    }
    for item in tc_items:
        new_vars['selected'] = item.id
        parent =  design
        for node_name in [item.axle_position, item.axle_sequence, item.wheel_side]:
            node = parent.get(node_name)
            if not node:
                node = dict()
                parent[node_name] = node
            parent = node

        sel_index = 1 if item.id == item_selected else 0
        side_or_steppe = 'steppe' if item.axle_position == 'steppe' else item.wheel_side

        if is_manage:
            select_tire = A(
                IMG(_style=img_style,_src=_static_url('images/tire_control/wheel/%s.png'%wheels[side_or_steppe]['out'][sel_index])),
                _href=URL(vars=new_vars))
            manage_tire = A(
                IMG(_style=img_style,_src=_static_url('images/tire_control/wheel/%s.png'%wheels[side_or_steppe]['in'][sel_index])),
                _href=URL(vars=new_vars))
        else:
            select_tire = IMG(_style=img_style,_src=_static_url('images/tire_control/wheel/%s.png'%wheels[side_or_steppe]['out'][sel_index]))
            manage_tire = IMG(_style=img_style,_src=_static_url('images/tire_control/wheel/%s.png'%wheels[side_or_steppe]['in'][sel_index]))

        parent[item.wheel_position] = manage_tire if item.tire_id else select_tire
    return design



@auth.requires(lambda: auth_has_access())
def axle():
    oform = ONXFORM(db.axle)
    oform.view_layout = 'others/form_children.html'
    oform.child_controls = True
    oform.save_and_add_enabled = False
    content = oform.get_current_action()
    breadcrumbs_add()

    children = [LOAD(c='tire_control', f='axle_wheel.load', args=['list',request.args(1)], ajax=True, content=loading)]
    content['children'] = children
    return content


def axle_wheel():
    try:
        action = request.args(0)
        parent_id = int(request.args(1))
        item_id = int(request.args(2) or 0)
        table_item = db.axle_wheel
        target = request.function
        list_url = URL(f=target+'.load', args=['list', parent_id])

        def _do_get_content(*args):
            if action == 'list':
                rows = db(table_item.axle_id==parent_id).select()
                for row in rows:
                    ONXREPR.row_repr(row, table_item)
                return rows
            elif action == 'edit':
                response.view = 'others/generic_modal.load'
                table_item.axle_id.default = parent_id
                table_item.axle_id.writable = False
                form = SQLFORM(table_item, item_id, formstyle=formstyle_onx)
                return form

        content = ONXFORM.child_item(action, parent_id, item_id, table_item,
            target, list_url, _do_get_content)
        return content
    except Exception, e:
        response.view = 'others/load_error.html'
        return dict(msg=str(e) )


@auth.requires(lambda: auth_has_access())
def chassi():
    oform = ONXFORM(db.chassi)
    oform.view_layout = 'others/form_children.html'
    oform.child_controls = True
    oform.save_and_add_enabled = False
    content = oform.get_current_action()
    breadcrumbs_add()

    children = [LOAD(c='tire_control', f='chassi_axle.load', args=['list',request.args(1)], ajax=True, content=loading)]
    content['children'] = children
    return content


def chassi_axle():
    try:
        action = request.args(0)
        parent_id = int(request.args(1))
        item_id = int(request.args(2) or 0)
        table_item = db.chassi_axle
        target = request.function
        list_url = URL(f=target+'.load', args=['list', parent_id])

        def _do_get_content(*args):
            if action == 'list':
                rows = db(table_item.chassi_id==parent_id).select()
                for row in rows:
                    ONXREPR.row_repr(row, table_item)
                return rows
            elif action == 'edit':
                table_item.chassi_id.default = parent_id
                table_item.chassi_id.writable = False
                form = SQLFORM(table_item, item_id, formstyle=formstyle_onx)
                return form

        content = ONXFORM.child_item(action, parent_id, item_id, table_item,
            target, list_url, _do_get_content)
        return content
    except Exception, e:
        response.view = 'others/load_error.html'
        return dict(msg=str(e) )


@auth.requires(lambda: auth_has_access())
def create():
    try:
        vehicle_id = int( request.vars['vehicle'] )
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=str(e) )

    def do_form_success(form):
        id = int(form.vars['id'])
        TireControlModel.change_chassi(id)
        return

    db.tire_control.vehicle_id.default = vehicle_id
    db.tire_control.vehicle_id.writable = False

    oform = ONXFORM(db.tire_control)
    oform.save_and_add_enabled = False
    oform.customize.on_form_success = do_form_success
    content = oform.execute_action('new', 0)

    breadcrumbs_add()
    return content


@auth.requires(lambda: auth_has_access())
def manage():

    def _get_tire_controls(item_id):
        if item_id == 0:
            return []

        controls = []
        new_vars = clear_vars_navegate(request.get_vars)
        item = db(db.tire_control_item.id == item_id).select().first()
        if item.tire_id:
            controls += [LOAD(c='tire_control', f='selected_tire.load', args=[item.id], vars=new_vars, ajax=True, content=loading)]
            controls += [LOAD(c='inventory', f='life_cycle.load', args=[item.tire_id], vars=new_vars, ajax=True, content=loading)]
        else:
            new_vars['owner_link'] = current_url()
            controls += [LOAD(f='select_tire.load', args=[item_selected], vars=new_vars, ajax=True, content=loading)]
        return controls

    try:
        vehicle_id = int( request.vars['vehicle'] )
        tire_option = request.vars.get('option')
        item_selected = int( request.vars.get('selected', 0) )
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=str(e) )

    bc = session.breadcrumbs

    control_query = (db.tire_control.vehicle_id == vehicle_id) \
        & (db.vehicle.id == db.tire_control.vehicle_id) \
        & (db.chassi.id == db.tire_control.chassi_id)
    control = db(control_query).select().first()
    if not control:
        new_vars = clear_vars_navegate(request.get_vars)
        new_vars['next'] = current_url()
        new_vars['previous'] = bc.last_url()
        redirect(URL(f='create', vars=new_vars))

    ONXREPR.row_repr(control.vehicle, db.vehicle)

    design = _get_chassi_design(control.tire_control.id, item_selected, True)
    tire_controls = _get_tire_controls(item_selected)

    table = _get_chassi_table(design)

    bc_parts = bc.last_url_parts()
    if bc_parts['function'] == 'create':
        bc.delete_current()
    breadcrumbs_add(T('Tire Control'))
    return dict(control=control, design=design, tire_controls=tire_controls, table=table)


@auth.requires(auth.has_membership(role=ADMIN_ROLE))
def change_chassi():
    try:
        vehicle_id = int( request.vars['vehicle'] )
        control = db((db.tire_control.vehicle_id == vehicle_id) ).select().first()
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=str(e) )

    def do_form_success(form):
        chassi_id = int(form.vars['chassi_id'])
        if chassi_id != control.chassi_id:
            TireControlModel.change_chassi(control.id)
        return

    db.tire_control.vehicle_id.default = vehicle_id
    db.tire_control.vehicle_id.writable = False

    oform = ONXFORM(db.tire_control)
    oform.save_and_add_enabled = False
    oform.customize.on_form_success = do_form_success
    content = oform.execute_action('update', control.id)

    response.page_alerts.append((
        T('Warning!'),
        T('When performing the change of chassi all information will be lost.'),
        'warning'))
    breadcrumbs_add()
    return content


def select_tire():
    try:
        item_id = int( request.args[0] )
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=str(e) )

    item = db(db.tire_control_item.id == item_id).select().first()
    ONXREPR.row_repr(item, db.tire_control_item)

    axle_info = Field('axle_info', writable=False, label=T('Axle'),
        default=T('Position %(axle_position)s, Sequence %(axle_sequence)s') % item.repr)
    wheel_info = Field('wheel_info', writable=False, label=T('Wheel'),
        default=T('Side %(wheel_side)s, Position %(wheel_position)s') % item.repr)
    db.tire_control_item.tire_id.requires = IS_IN_DB(db((db.inventory_item.item_type == 'tire') \
        & (db.inventory_item.status == 'available')),
        db.inventory_item, db.inventory_item._format)
    db.tire_control_item.tire_id.width_lookup = '80%'

    vehicle = db.vehicle[item.vehicle_id]
    VehicleModel.default_odometer(
        field=db.tire_control_item.start_odometer,
        vehicle=vehicle,
        default=vehicle.current_odometer,
        start_range=0.0
        )

    form = SQLFORM.factory(
        axle_info, wheel_info,
        db.tire_control_item.start_date,
        db.tire_control_item.tire_id,
        db.tire_control_item.start_odometer,
        submit_button=T('Select'),
        formstyle=formstyle_onx)
    if form.process(formname='select_tire_form').accepted:
        tire_id = int(form.vars['tire_id'])
        start_odometer = float(form.vars['start_odometer'])
        start_date = form.vars['start_date']
        owner_link = request.vars.get('owner_link')
        #change to in_use
        InventoryModel.change_item_status(tire_id, 'in_use', 'tire_control_item', item_id, owner_link)
        #update odometer
        VehicleModel.vehicle_odometer_change(
            vehicle_id=vehicle.id,
            odometer_status='normal',
            odometer=start_odometer,
            note=T('Start tire control'),
            owner_table='tire_control_item',
            owner_key=item.id,
            owner_link=owner_link)
        #update control
        vehicle = db.vehicle[item.vehicle_id]
        if start_odometer >= vehicle.current_odometer:
            start_control = vehicle.accumulated_odometer
        else:
            start_control = vehicle.accumulated_odometer - (vehicle.current_odometer - start_odometer)
        item.update_record(
            tire_id=tire_id,
            start_date=start_date,
            start_odometer=start_odometer,
            start_control=start_control)

        response.js = """
            window.location.reload(true);
            """
    return dict(content=form)


def selected_tire():
    try:
        item_id = int( request.args[0] )
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=str(e) )

    item = db.tire_control_item[item_id]
    ONXREPR.row_repr(item, db.tire_control_item)

    #vehicle = db.vehicle[item.vehicle_id]
    #item.repr.distance = vehicle.accumulated_odometer - item.start_control

    return dict(record=item)


@auth.requires(lambda: auth_has_access())
def remove_tire():
    try:
        item_id = int( request.args[0] )
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=str(e) )

    item = db(db.tire_control_item.id == item_id).select().first()
    tire_id = item.tire_id
    item.update_record(tire_id=None)
    InventoryModel.change_item_status(tire_id, 'available', None, None, None)
    response.js = """
        window.location.reload(true);
        """
    return

@auth.requires(lambda: auth_has_access())
def groove_annotation_print():
    try:
        tire_control_id = int( request.args[0] )
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=str(e) )

    tc_items = db(db.tire_control_item.tire_control_id == tire_control_id).select(orderby=tc_items_order)

    head = THEAD(TR(
            TH(T('Axle'),_width="25%"),
            TH(T('Wheel'),_width="25%"),
            TH(T('Tire'),_width="40%"),
            TH(T('Groove'),_width="10%"),
            _bgcolor="#A0A0A0"))
    rows = []
    for i, item in enumerate(tc_items):
        col = i % 2 and "#F0F0F0" or "#FFFFFF"
        ONXREPR.row_repr(item, db.tire_control_item)
        rows.append(TR(
            TD('%(axle_position)s, %(axle_sequence)s' % item.repr),
            TD('%(wheel_side)s, %(wheel_position)s' % item.repr),
            TD('%(tire_id)s' % item.repr),
            TD(' '),
            _bgcolor=col))

    body = TBODY(*rows)
    table = TABLE(*[head, body],
                  _border="1", _align="center", _width="100%")

    control = db(db.tire_control.id == tire_control_id).select().first()
    ONXREPR.row_repr(control, db.tire_control)

    from gluon.contrib.pyfpdf import FPDF, HTMLMixin
    class MyFPDF(FPDF, HTMLMixin):
        def header(self):
            self.set_font('Arial','B',15)
            self.cell(0,10, control.repr.vehicle_id ,1,0,'C')
            self.ln(20)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial','I',8)
            txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(0,10,txt,0,0,'C')

    pdf=MyFPDF()
    pdf.add_page()
    pdf.write_html(str(XML(table, sanitize=False)))

    tmpfilename=os.path.join(request.folder,'private',str(uuid.uuid4()))
    pdf.output(name=tmpfilename, dest='F')
    data = open(tmpfilename,"rb").read()
    os.unlink(tmpfilename)
    response.headers['Content-Type']='application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename="groove_annotation.pdf"'
    return data


def tire_groove():
    try:
        action = request.args(0)
        parent_id = int(request.args(1))
        item_id = int(request.args(2) or 0)
        table_item = db.groove_annotation
        target = request.function
        list_url = URL(c='tire_control', f=target+'.load', args=['list', parent_id])

        def _do_get_content(*args):
            if action == 'list':
                rows = db(table_item.tire_id==parent_id).select()
                for row in rows:
                    ONXREPR.row_repr(row, table_item)
                return rows
            elif action == 'edit':
                response.view = 'others/generic_modal.load'
                parent = db.inventory_item[parent_id]
                if parent.status == 'available':
                    table_item.vehicle_id.writable = False
                    table_item.vehicle_id.readable = False
                    table_item.old_odometer.writable = False
                    table_item.old_odometer.readable = False
                    table_item.odometer.writable = False
                    table_item.odometer.readable = False
                    table_item.distance.writable = False
                    table_item.distance.readable = False

                table_item.tire_id.default = parent_id
                table_item.tire_id.writable = False

                form = SQLFORM(table_item, item_id, formstyle=formstyle_onx)
                return form

        content = ONXFORM.child_item(action, parent_id, item_id, table_item,
            target, list_url, _do_get_content)
        return content
    except Exception, e:
        response.view = 'others/load_error.html'
        return dict(msg=str(e) )


@auth.requires(lambda: auth_has_access())
def groove_annotation():
    try:
        tc_id = int( request.args[0] )
    except Exception, e:
        response.view = 'others/gadget_error.html'
        return dict(msg=str(e) )

    tc = db(db.tire_control.id == tc_id).select().first()
    ONXREPR.row_repr(tc, db.tire_control)

    fields = []
    tc_items = db(db.tire_control_item.tire_control_id == tc_id).select(orderby=tc_items_order)
    for item in tc_items:
        ONXREPR.row_repr(item, db.tire_control_item)
        if item.tire_id:
            fields.append(Field('groove_%s'%item.id, 'double'))
            fields.append(Field('note_%s'%item.id, 'string'))

    fields.append(db.groove_annotation.old_odometer)
    fields.append(db.groove_annotation.odometer)
    fields.append(db.groove_annotation.distance)

    form = SQLFORM.factory(*fields, _class='form-horizontal onx-form')
    if form.process().accepted:
        defs = table_default_values(db.groove_annotation)
        for item in filter(lambda it: it.tire_id, tc_items):
            defs['tire_id'] = item.tire_id
            defs['groove'] = float(form.vars['groove_%s'%item.id])
            defs['note'] = form.vars['note_%s'%item.id]
            defs['vehicle_id'] = tc.vehicle_id
            defs['old_odometer'] = float(form.vars['old_odometer'])
            defs['odometer'] = float(form.vars['odometer'])
            defs['distance'] = float(form.vars['distance'])
            db.groove_annotation.insert(**defs)
        redirect(URL(c='tire_control', f='manage', vars=request.get_vars))

    response.title = T('Groove Annotation')
    breadcrumbs_add(response.title)
    return dict(tc=tc, tc_items=tc_items, form=form)