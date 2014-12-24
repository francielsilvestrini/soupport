# -*- coding: utf-8 -*-

def crud(table):
    content = ONXFORM.make(table)
    breadcrumbs_add()
    return content

@auth.requires(lambda: auth_has_access())
def unit_of_measure():
    return crud(db.O1_unit_of_measure)

@auth.requires(lambda: auth_has_access())
def system():
    return crud(db.O1_system)

@auth.requires(lambda: auth_has_access())
def subsystem():
    return crud(db.O1_subsystem)

@auth.requires(lambda: auth_has_access())
def system_item():
    return crud(db.O1_system_item)


@auth.requires(lambda: auth_has_access())
def inventory_item():

    def do_form_success(form):
        id = int(form.vars['id'])
        item_type = form.vars['item_type']
        if item_type == 'tire' \
        and db(db.O3_groove_annotation.tire_id == id).count() == 0:
            O3Model.initial_groove(id)
        return    

    try:
        action = getlist(request.args, 0)
        record_id = 0 if action == 'new' else int(getlist(request.args, 1, 0))
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg=T('ERROR: %s') % str(e) )

    oform = ONXFORM(db.O1_inventory_item)
    oform.view_layout = 'inventory/inventory_item.html'
    oform.child_controls = True
    oform.customize.on_form_success = do_form_success
    content = oform.get_current_action()
    breadcrumbs_add()

    children = []
    if action in['update', 'read']:
        record = db.O1_inventory_item[record_id]
        if record.item_type == 'tire':
            children += [LOAD(c='tire_control', f='tire_groove.load', args=['list', record_id], ajax=True, content=loading)]
    children += [LOAD(c='inventory', f='usage_history.load', args=['list',record_id], ajax=True, content=loading)]
    content['children'] = children
    return content


def usage_history():
    try:
        action = request.args(0)
        parent_id = int(request.args(1))
        item_id = int(request.args(2) or 0)
        table_item = db.O1_usage_history
        target = request.function
        list_url = URL(f=target+'.load', args=['list', parent_id])

        def _do_get_content(*args):
            if action == 'list':
                rows = db(table_item.item_id==parent_id).select(orderby=~table_item.usage_start, limitby=(0,10))
                for row in rows:
                    ONXREPR.row_repr(row, table_item)
                    if row.owner_table == 'O2_vehicle':
                        row.repr.owner_key = '%(licence_plate)s - %(description)s' % db.O2_vehicle[int(row.owner_key)]
                return rows


        content = ONXFORM.child_item(action, parent_id, item_id, table_item,
            target, list_url, _do_get_content)
        return content
    except Exception, e:
        response.view = 'others/load_error.html'        
        return dict(msg=str(e) )


@auth.requires(lambda: auth_has_access())
def components():
    try:
        owner_table = request.args[0]
        owner_key = request.args[1]
        item_selected = int( request.vars.get('selected', 0) )
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg=T('ERROR: %s') % str(e) )

    caption = DIV(T('Components'), _style='padding-top:10px;')
    if owner_table == 'O2_vehicle':
        vehicle = db(db.O2_vehicle.id == int(owner_key)).select().first()
        caption = DIV(A(vehicle.licence_plate, SMALL(' '+vehicle.description), 
            _href=URL(c='fleet', f='vehicle', args=['read', vehicle.id])), _class='brand')

    items = db((db.O1_component_item.owner_table == owner_table) & (db.O1_component_item.owner_key == owner_key)).select()
    for item in items:
        ONXREPR.row_repr(item, db.O1_component_item)

    controls = []
    if db(db.O1_component_item.id == item_selected).count() > 0:
        controls += [LOAD(c='inventory', f='selected_component.load', args=[item_selected], vars=request.get_vars, ajax=True, content=loading)]
        controls += [LOAD(c='inventory', f='life_cycle.load', args=[item_selected], vars=request.get_vars, ajax=True, content=loading)]

    content = dict(
        caption=caption,
        items=items, 
        controls=controls
        )

    breadcrumbs_add(T('Components'))
    return content


def add_component():
    try:
        owner_table = request.args[0]
        owner_key = request.args[1]
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg=T('ERROR: %s') % str(e) )

    avaliable_components = (db.O1_inventory_item.item_type == 'component') & (db.O1_inventory_item.status == 'available')
    db.O1_component_item.component_id.requires = IS_IN_DB(db(avaliable_components), db.O1_inventory_item, db.O1_inventory_item._format)

    form = SQLFORM.factory(
        db.O1_component_item.component_id,
        _class='form-horizontal onx-form',
        buttons=[ONXFORM.get_btn_save()],
        formstyle=formstyle_onx)
    if form.process(formname='add_component_form').accepted:
        component_id = int(form.vars['component_id'])
        owner_link = None
        if owner_table == 'O2_vehicle':
            owner_link = URL(c='fleet', f='vehicle.html', args=['read', owner_key])            
        defs = table_default_values(db.O1_component_item)
        defs['component_id'] = component_id
        defs['owner_table'] = owner_table
        defs['owner_key'] = owner_key
        defs['owner_link'] = owner_link
        
        db.O1_component_item.insert(**defs)
        O1Model.change_item_status(component_id, 'in_use', owner_table, owner_key, owner_link)

        response.js = """
            window.location.reload(true);
            """
    response.view = 'others/generic_modal.load'
    return dict(content=form)


def selected_component():
    try:
        item_id = int( request.args[0] )
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg=T('ERROR: %s') % str(e) )

    item = db((db.O1_component_item.id == item_id) \
        & (db.O1_inventory_item.id == db.O1_component_item.component_id)
        ).select().first()
    ONXREPR.row_repr(item.O1_component_item, db.O1_component_item)
    ONXREPR.row_repr(item.O1_inventory_item, db.O1_inventory_item)
    return dict(record=item)


@auth.requires(lambda: auth_has_access())
def remove_component():
    try:
        item_id = int( request.args[0] )
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg=T('ERROR: %s') % str(e) )

    item = db(db.O1_component_item.id == item_id).select().first()
    component_id = item.component_id
    db(db.O1_component_item.id == item_id).delete()
    O1Model.change_item_status(component_id, 'available', None, None, None)
    response.js = """
        window.location.reload(true);
        """
    return

def life_cycle():
    try:
        item_id = int( request.args[0] )
    except Exception, e:
        response.view = 'others/gadget_error.html'        
        return dict(msg=str(e) )
    return dict()    