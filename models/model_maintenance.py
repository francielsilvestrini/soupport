# -*- coding: utf-8 -*-

from onx_files import csv_defaults

class MaintenanceModel(ModelBase):
    name = 'maintenance'

    def __init__(self):
        ModelBase.__init__(self)
        self.crud_controller = 'maintenance'
        return

    def define_tables(self):

        self.cruds += ['maintenance_service']
        db.define_table('maintenance_service',
            Field('subsystem_id', db.subsystem, label=T('Subsystem')),
            Field('name', 'string', label=T('Name')),
            Field('maintenance_interval', 'double', label=T('Interval')),
            Field('notify_with', 'double', label=T('Notify With')),
            Field('is_active', 'boolean', label=T('Active')),
            migrate='maintenance_service.table',
            format='%(name)s')
        db.maintenance_service.subsystem_id.requires = IS_IN_DB(db, db.subsystem, db.subsystem._format)
        db.maintenance_service.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'maintenance_service.name')]
        db.maintenance_service.maintenance_interval.default = 5000.00
        db.maintenance_service.notify_with.default = 500.00
        db.maintenance_service.is_active.default = True


        self.cruds += ['maintenance_plan']
        db.define_table('maintenance_plan',
            Field('name', 'string', label=T('Name')),
            migrate='maintenance_plan.table',
            format='%(name)s')
        db.maintenance_plan.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'maintenance_plan.name')]


        db.define_table('maintenance_plan_item',
            Field('plan_id', db.maintenance_plan, label=T('Maintenance Plan'), writable=False),
            Field('service_id', db.maintenance_service, label=T('Service')),
            Field('maintenance_interval', 'double', label=T('Interval')),
            Field('notify_with', 'double', label=T('Notify With')),
            migrate='maintenance_plan_item.table',
            format='%(id)s')
        db.maintenance_plan_item.plan_id.requires = IS_IN_DB(db, db.maintenance_plan, db.maintenance_plan._format)
        db.maintenance_plan_item.service_id.requires = IS_IN_DB(db, db.maintenance_service, db.maintenance_service._format)
        db.maintenance_plan_item.service_id.widget = LookupWidget(width='85%', add_new=URL(c='maintenance', f='maintenance_service', args='new')).widget


        db.define_table('maintenance_control',
            Field('vehicle_id', db.vehicle, label=T('Vehicle'), writable=False),
            Field('plan_id', db.maintenance_plan, label=T('Maintenance Plan')),
            migrate='maintenance_control.table',
            format='%(id)s')
        db.maintenance_control.vehicle_id.requires = IS_IN_DB(db, db.vehicle, db.vehicle._format)
        db.maintenance_control.plan_id.requires = IS_IN_DB(db, db.maintenance_plan, db.maintenance_plan._format)
        db.maintenance_control.plan_id.widget = LookupWidget(add_new=URL(c='maintenance', f='maintenance_plan', args='new')).widget

        db.define_table('maintenance_control_item',
            Field('control_id', db.maintenance_control, label=T('Maintenance Control'), writable=False, readable=False),
            Field('vehicle_id', db.vehicle, label=T('Vehicle'), writable=False),
            Field('service_id', db.maintenance_service, label=T('Service')),
            Field('maintenance_interval', 'double', label=T('Interval')),
            Field('notify_with', 'double', label=T('Notify With')),
            Field('last_maintenance', 'double', label=T('Last Maintenance')),
            Field('next_maintenance', 'double', label=T('Next Maintenance')),

            migrate='maintenance_control_item.table',
            format='%(id)s')
        db.maintenance_control_item.control_id.requires = IS_IN_DB(db, db.maintenance_control, db.maintenance_control._format)
        db.maintenance_control_item.vehicle_id.requires = IS_IN_DB(db, db.vehicle, db.vehicle._format)
        db.maintenance_control_item.service_id.requires = IS_IN_DB(db, db.maintenance_service, db.maintenance_service._format)
        db.maintenance_control_item.service_id.widget = LookupWidget(width='90%').widget

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
            defs['notify_with'] = item.notify_with
            defs['last_maintenance'] = last_maintenance
            defs['next_maintenance'] = last_maintenance + item.maintenance_interval
            db.maintenance_control_item.insert(**defs)
        return


    @staticmethod
    def odometer_reseted(vehicle_id, odometer):
        items = db(db.maintenance_control_item.vehicle_id == vehicle_id).select().first()
        for item in items:
            new = item.next_maintenance - odometer
            item.update_record(last_maintenance=0.0, next_maintenance=new)
        return

    # END BUSINESS RULES
    #--------------------------------------------------------------------------


