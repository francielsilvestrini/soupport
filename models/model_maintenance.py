# -*- coding: utf-8 -*-

from onx_files import csv_defaults

class MaintenanceModel(ModelBase):
    name = 'maintenance'

    maintenance_order_status = {
        'open': T('Open'),
        'canceled': T('Canceled'),
        'finalized': T('Finalized'),
    }


    @staticmethod
    def maintenance_service_lookup(field, default):
        wgt = LookupWidget(
            add_new=lookup_url_new(c='maintenance', f='maintenance_service')
            ).widget(field, default)
        return wgt

    @staticmethod
    def maintenance_plan_lookup(field, default):
        wgt = LookupWidget(
            add_new=lookup_url_new(c='maintenance', f='maintenance_plan')
            ).widget(field, default)
        return wgt

    def define_tables(self):

        db.define_table('maintenance_service',
            Field('subsystem_id', db.subsystem, label=T('Subsystem')),
            Field('name', 'string', label=T('Name')),
            Field('maintenance_interval', 'double', label=T('Interval')),
            Field('is_active', 'boolean', label=T('Active')),
            migrate='maintenance_service.table',
            format='%(name)s')
        db.maintenance_service.subsystem_id.requires = IS_IN_DB(db, db.subsystem, db.subsystem._format)
        db.maintenance_service.subsystem_id.widget = InventoryModel.subsystem_lookup
        db.maintenance_service.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'maintenance_service.name')]
        db.maintenance_service.maintenance_interval.default = 5000.00
        db.maintenance_service.is_active.default = True
        self.cruds += [dict(c='maintenance', f='maintenance_service')]


        db.define_table('maintenance_plan',
            Field('name', 'string', label=T('Name')),
            migrate='maintenance_plan.table',
            format='%(name)s')
        db.maintenance_plan.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'maintenance_plan.name')]
        self.cruds += [dict(c='maintenance', f='maintenance_plan')]


        db.define_table('maintenance_plan_item',
            Field('plan_id', db.maintenance_plan, label=T('Maintenance Plan'), writable=False),
            Field('service_id', db.maintenance_service, label=T('Service')),
            Field('maintenance_interval', 'double', label=T('Interval')),
            migrate='maintenance_plan_item.table',
            format='%(id)s')
        db.maintenance_plan_item.plan_id.requires = IS_IN_DB(db, db.maintenance_plan, db.maintenance_plan._format)
        db.maintenance_plan_item.service_id.requires = IS_IN_DB(db, db.maintenance_service, db.maintenance_service._format)
        db.maintenance_plan_item.service_id.width_lookup = '85%'
        db.maintenance_plan_item.service_id.widget = MaintenanceModel.maintenance_service_lookup


        db.define_table('maintenance_control',
            Field('vehicle_id', db.vehicle, label=T('Vehicle'), writable=False),
            Field('plan_id', db.maintenance_plan, label=T('Maintenance Plan')),
            migrate='maintenance_control.table',
            format='%(id)s')
        db.maintenance_control.vehicle_id.requires = IS_IN_DB(db, db.vehicle, db.vehicle._format)
        db.maintenance_control.plan_id.requires = IS_IN_DB(db, db.maintenance_plan, db.maintenance_plan._format)
        db.maintenance_control.plan_id.widget = MaintenanceModel.maintenance_plan_lookup


        db.define_table('maintenance_control_item',
            Field('control_id', db.maintenance_control, label=T('Maintenance Control'), writable=False, readable=False),
            Field('vehicle_id', db.vehicle, label=T('Vehicle'), writable=False),
            Field('service_id', db.maintenance_service, label=T('Service')),
            Field('maintenance_interval', 'double', label=T('Interval')),
            Field('last_maintenance', 'double', label=T('Last Maintenance')),
            Field('next_maintenance', 'double', label=T('Next Maintenance')),
            migrate='maintenance_control_item.table',
            format='%(id)s')
        db.maintenance_control_item.control_id.requires = IS_IN_DB(db, db.maintenance_control, db.maintenance_control._format)
        db.maintenance_control_item.vehicle_id.requires = IS_IN_DB(db, db.vehicle, db.vehicle._format)
        db.maintenance_control_item.service_id.requires = IS_IN_DB(db, db.maintenance_service, db.maintenance_service._format)
        db.maintenance_control_item.service_id.width_lookup = '80%'
        db.maintenance_control_item.service_id.widget = MaintenanceModel.maintenance_service_lookup


        db.define_table('maintenance_order',
            Field('vehicle_id', db.vehicle, label=T('Vehicle')),
            Field('current_odometer', 'double', label=T('Odometer Current')),
            Field('supplier_id', db.person, label=T('Supplier')),
            Field('invoice_number', 'string', label=T('Invoice Number')),
            Field('order_date', 'date', label=T('Date')),
            Field('status', 'string', label=T('Status')),
            Field('services', 'double', label=T('Services')),
            Field('materials', 'double', label=T('Materials')),
            Field('discount', 'double', label=T('Discount')),
            Field('total_order', 'double', label=T('Total')),

            migrate='maintenance_order.table',
            format=str(T('Order #%(id)s')))
        db.maintenance_order.vehicle_id.requires = IS_IN_DB(db, db.vehicle, db.vehicle._format)
        db.maintenance_order.supplier_id.requires = EntriesModel.person_IS_IN_DB(types='supplier')
        db.maintenance_order.supplier_id.widget = LookupWidget().widget
        db.maintenance_order.order_date.default = request.now.today()
        db.maintenance_order.status.requires = IS_IN_SET(MaintenanceModel.maintenance_order_status)
        db.maintenance_order.status.represent = lambda value, row: MaintenanceModel.maintenance_order_status.get(value) or value
        db.maintenance_order.status.default = 'open'
        db.maintenance_order.services.default = 0.0
        db.maintenance_order.materials.default = 0.0
        db.maintenance_order.discount.default = 0.0
        db.maintenance_order.total_order.default = 0.0


        def _maintenance_order_services_format(row):
            service = db(db.maintenance_service.id == row.service_id).select().first()
            text = service.name
            if row.description and row.description != '':
                text = '%s /%s' % (service.name, row.description)
            return text

        db.define_table('maintenance_order_services',
            Field('order_id', db.maintenance_order, label=T('Maintenance Order'), writable=False, readable=False),
            Field('service_id', db.maintenance_service, label=T('Service')),
            Field('description', 'string', label=T('Description')),
            Field('cost', 'double', label=T('Cost')),
            Field('maintenance_interval', 'double', label=T('Interval')),
            Field('next_maintenance', 'double', label=T('Next Maintenance')),
            migrate='maintenance_order_services.table',
            format=_maintenance_order_services_format)
        db.maintenance_order_services.order_id.requires = IS_IN_DB(db, db.maintenance_order, db.maintenance_order._format)
        db.maintenance_order_services.service_id.requires = IS_IN_DB(db, db.maintenance_service, db.maintenance_service._format)
        db.maintenance_order_services.service_id.width_lookup = '85%'
        db.maintenance_order_services.service_id.widget = MaintenanceModel.maintenance_service_lookup
        db.maintenance_order_services.cost.default = 0.0
        db.maintenance_order_services.maintenance_interval.default = 0.0
        db.maintenance_order_services.next_maintenance.default = 0.0


        db.define_table('maintenance_order_materials',
            Field('order_id', db.maintenance_order, label=T('Maintenance Order'), writable=False, readable=False),
            Field('material_id', db.inventory_item, label=T('Material')),
            Field('description', 'string', label=T('Description')),
            Field('quantity', 'double', label=T('Quantity')),
            Field('unit_cost', 'double', label=T('Unit Cost')),
            Field('discount', 'double', label=T('Discount')),
            Field('total_cost', 'double', label=T('Total Cost')),
            Field('add_to_stock', 'double', label=T('Add to Stock')),
            Field('add_to_order', 'double', label=T('Add to Order')),
            Field('service_reference_id', db.maintenance_order_services, label=T('Service Reference')),
            migrate='maintenance_order_materials.table',
            format='%(id)s')
        db.maintenance_order_materials.order_id.requires = IS_IN_DB(db, db.maintenance_order, db.maintenance_order._format)
        db.maintenance_order_materials.material_id.requires = InventoryModel.item_IS_IN_DB(status='available', item_type='material')
        db.maintenance_order_materials.material_id.widget = InventoryModel.inventory_item_lookup
        db.maintenance_order_materials.material_id.width_lookup = '85%'
        db.maintenance_order_materials.quantity.default = 1.0
        db.maintenance_order_materials.unit_cost.default = 0.0
        db.maintenance_order_materials.discount.default = 0.0
        db.maintenance_order_materials.total_cost.default = 0.0
        db.maintenance_order_materials.add_to_stock.default = 0.0
        db.maintenance_order_materials.add_to_order.default = 0.0
        db.maintenance_order_materials.service_reference_id.widget = LookupWidget().widget
        db.maintenance_order_materials.service_reference_id.width_lookup = '85%'
        return


    def create_defaults(self):
        tables = {}
        tables['maintenance_service'] = self.default_maintenance_service

        for k in tables:
            if db(db[k]).isempty():
                tables[k]()
        return


    def default_maintenance_service(self):
        reader = csv_defaults('maintenance_service.csv')
        if not reader:
            return

        defs = table_default_values(db.maintenance_service)
        cols = Dict(name=0,subsystem=1)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            subsystem = db(db.subsystem.name == row[cols['subsystem']]).select().first()
            if not subsystem:
                continue
            defs['subsystem_id'] = subsystem.id
            defs['name'] = row[cols['name']]

            db.maintenance_service.update_or_insert(
                db.maintenance_service.name==defs['name'], **defs)


    #--------------------------------------------------------------------------
    # BEGIN BUSINESS RULES

    @staticmethod
    def change_plan(control_id, plan_id, last_maintenance):
        plan_items = db(db.maintenance_plan_item.plan_id == plan_id).select()
        control = db(db.maintenance_control.id == control_id).select().first()

        for item in plan_items:
            defs = table_default_values(db.maintenance_control_item)
            defs['control_id'] = control.id
            defs['vehicle_id'] = control.vehicle_id
            defs['service_id'] = item.service_id
            defs['maintenance_interval'] = item.maintenance_interval
            defs['last_maintenance'] = last_maintenance
            defs['next_maintenance'] = last_maintenance + item.maintenance_interval
            db.maintenance_control_item.insert(**defs)
        return


    @staticmethod
    def odometer_reseted(vehicle_id, odometer):
        items = db(db.maintenance_control_item.vehicle_id == vehicle_id).select()
        for item in items:
            new = item.next_maintenance - odometer
            item.update_record(last_maintenance=0.0, next_maintenance=new)
        return

    @staticmethod
    def update_maintenance(vehicle_id, service_id, last_maintenance, maintenance_interval, next_maintenance):
        control = db(db.maintenance_control.vehicle_id == vehicle_id).select().first()
        items = db((db.maintenance_control_item.vehicle_id == vehicle_id) \
            & (db.maintenance_control_item.service_id == service_id)).select()

        if len(items) == 0:
            defs = table_default_values(db.maintenance_control_item)
            defs['control_id'] = control.id
            defs['vehicle_id'] = control.vehicle_id
            defs['service_id'] = service_id
            defs['maintenance_interval'] = maintenance_interval
            defs['last_maintenance'] = last_maintenance
            defs['next_maintenance'] = next_maintenance
            db.maintenance_control_item.insert(**defs)
        else:
            for item in items:
                item.update_record(
                    maintenance_interval=maintenance_interval,
                    last_maintenance=last_maintenance,
                    next_maintenance=next_maintenance)

        return

    # END BUSINESS RULES
    #--------------------------------------------------------------------------


