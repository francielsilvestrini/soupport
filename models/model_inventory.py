# -*- coding: utf-8 -*-

from onx_files import csv_defaults

class InventoryModel(ModelBase):
    name = 'inventory'

    system_item_type = {
        'fuel':T('Fuel'),
        'lubricant':T('Lubricant'),
        'material':T('Material'),
        'pneu':T('Pneu'),
        'service':T('Service'),
        'expense':T('Expense'),
        }

    inventory_item_type = {
        'tire':T('Tire'),
        'component':T('Component'),
        'material':T('Material'),
        }

    inventory_item_status = {
        'available':T('Available'),
        'in_use':T('In Use'),
        'disuse':T('Disuse'),
        'sold':T('Sold'),
    }

    inventory_item_life_cycle_status = {
        'new':T('New'),
        'used':T('Used'),
    }


    @staticmethod
    def unit_of_measure_lookup(field, default):
        wgt = LookupWidget(
            add_new=lookup_url_new(c='inventory', f='unit_of_measure')
            ).widget(field, default)
        return wgt

    @staticmethod
    def system_lookup(field, default):
        wgt = LookupWidget(
            add_new=lookup_url_new(c='inventory', f='system')
            ).widget(field, default)
        return wgt

    @staticmethod
    def subsystem_lookup(field, default):
        wgt = LookupWidget(
            add_new=lookup_url_new(c='inventory', f='subsystem')
            ).widget(field, default)
        return wgt

    @staticmethod
    def system_item_lookup(field, default):
        wgt = LookupWidget(
            add_new=lookup_url_new(c='inventory', f='system_item')
            ).widget(field, default)
        return wgt

    @staticmethod
    def inventory_item_lookup(field, default):
        wgt = LookupWidget(
            add_new=lookup_url_new(c='inventory', f='inventory_item')
            ).widget(field, default)
        return wgt


    def define_tables(self):
        db.define_table('unit_of_measure',
            Field('acronym', 'string', label=T('Acronym')),
            Field('name', 'string', label=T('Name')),
            migrate='unit_of_measure.table',
            format='%(acronym)s - %(name)s')
        db.unit_of_measure.acronym.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'unit_of_measure.acronym')]
        db.unit_of_measure.name.requires = [IS_NOT_EMPTY()]


        db.define_table('system',
            Field('name', 'string', label=T('Name')),
            migrate='system.table',
            format='%(name)s')
        db.system.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'system.name')]


        def _subsystem_format(row):
            system = field_rep(db.subsystem.system_id, row.system_id, row)
            return '%s/%s' % (system, row.name)

        db.define_table('subsystem',
            Field('name', 'string', label=T('Name')),
            Field('system_id', db.system, label=T('System')),
            migrate='subsystem.table',
            format=lambda row:_subsystem_format(row))
        db.subsystem.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'subsystem.name')]
        db.subsystem.system_id.requires = IS_IN_DB(db, db.system, db.system._format)
        db.subsystem.system_id.widget = InventoryModel.system_lookup


        db.define_table('system_item',
            Field('name', 'string', label=T('Name')),
            Field('item_type', 'string', label=T('Type')),
            Field('subsystem_id', db.subsystem, label=T('Subsystem')),
            Field('unit_of_measure_id', db.unit_of_measure, label=T('Unit of Measure')),
            Field('is_active', 'boolean', label=T('Active')),
            migrate='system_item.table',
            format='%(name)s')
        db.system_item.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'system_item.name')]
        db.system_item.item_type.requires = IS_IN_SET(InventoryModel.system_item_type)
        db.system_item.item_type.represent = lambda value, row: InventoryModel.system_item_type[value]
        db.system_item.unit_of_measure_id.requires = IS_IN_DB(db, db.unit_of_measure, db.unit_of_measure._format)
        db.system_item.unit_of_measure_id.widget = InventoryModel.unit_of_measure_lookup
        db.system_item.subsystem_id.requires = IS_IN_DB(db, db.subsystem, db.subsystem._format)
        db.system_item.subsystem_id.widget = InventoryModel.subsystem_lookup
        db.system_item.is_active.default = True


        db.define_table('inventory_item',
            Field('number', 'string', label=T('Number')),
            Field('description', 'string', label=T('Description')),
            Field('item_type', 'string', label=T('Type')),
            Field('unit_of_measure_id', db.unit_of_measure, label=T('Unit of Measure')),
            Field('status', 'string', label=T('Status')),
            Field('material_id', db.system_item, label=T('Material')),
            Field('use_count', 'double', label=T('Use Count')),
            Field('initial_groove', 'double', label=T('Initial Groove')),
            Field('end_groove', 'double', label=T('End Groove')),
            #Field('life_cycle_status', 'string', label=T('Life Cycle Status')),
            #Field('life_cycle', 'integer', label=T('Life Cycle')),

            #Field('bio_brand', 'string', label=T('Brand')),
            #Field('bio_model', 'string', label=T('Model')),
            #Field('bio_design', 'string', label=T('Design')),
            #Field('bio_technical_inf', 'text', label=T('Technical Inf.')),#design|rubber type|numero de lonas|capacidade de carga
            #Field('bio_supplier_id', 'string', label=T('Supplier')),
            #Field('bio_purchase_date', 'string', label=T('Rubber')),
            #Field('bio_purchase_value', 'string', label=T('Rubber')),

            #Field('casualty_date', 'string', label=T('Rubber')),
            #Field('casualty_destination', 'string', label=T('Rubber')),
            #Field('casualty_reason', 'string', label=T('Rubber')),
            #Field('casualty_value', 'string', label=T('Rubber')),

            #owner_fields,
            migrate='inventory_item.table',
            format='%(number)s - %(description)s')
        db.inventory_item.number.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'inventory_item.number')]
        db.inventory_item.number.default = lambda: CommomModel.sequence_ticket('inventory_item', 'I-')
        db.inventory_item.description.requires = [IS_NOT_EMPTY()]
        db.inventory_item.item_type.requires = IS_IN_SET(InventoryModel.inventory_item_type)
        db.inventory_item.item_type.represent = lambda value, row: InventoryModel.inventory_item_type.get(value, value)
        db.inventory_item.unit_of_measure_id.requires = IS_IN_DB(db, db.unit_of_measure, db.unit_of_measure._format)
        db.inventory_item.unit_of_measure_id.widget = InventoryModel.unit_of_measure_lookup
        db.inventory_item.unit_of_measure_id.default = InventoryModel.unit_of_measure_default
        db.inventory_item.status.requires = IS_IN_SET(InventoryModel.inventory_item_status)
        db.inventory_item.status.represent = lambda value, row: InventoryModel.inventory_item_status.get(value, value)
        db.inventory_item.status.default = 'available'
        db.inventory_item.material_id.requires = IS_IN_DB(db(db.system_item.item_type == 'material'), db.system_item, db.system_item._format)
        db.inventory_item.material_id.widget = InventoryModel.system_item_lookup
        db.inventory_item.use_count.default = 0.0
        db.inventory_item.initial_groove.default = 10.0
        db.inventory_item.initial_groove.show_grid = False
        db.inventory_item.end_groove.default = 1.0
        db.inventory_item.end_groove.show_grid = False


        db.define_table('usage_history',
            Field('item_id', db.inventory_item, label=T('Item')),
            Field('usage_start', 'datetime', label=T('Start')),
            Field('usage_end', 'datetime', label=T('End')),
            Field('status_end', 'string', label=T('Status End')),
            owner_fields,
            migrate='usage_history.table',
            format='%(id)s')
        db.usage_history.item_id.requires = IS_IN_DB(db, db.inventory_item, db.inventory_item._format)
        db.usage_history.usage_start.default = request.now
        db.usage_history.status_end.requires = IS_IN_SET(InventoryModel.inventory_item_status)
        db.usage_history.status_end.represent = lambda value, row: InventoryModel.inventory_item_status.get(value, value or '')


        db.define_table('component_item',
            owner_fields,
            Field('component_id', db.inventory_item, label=T('Component')),
            migrate='component_item.table',
            format='%(id)s')
        db.component_item.component_id.requires = IS_IN_DB(db(db.inventory_item.item_type == 'component'), db.inventory_item, db.inventory_item._format)
        db.component_item.component_id.widget = LookupWidget(width='90%').widget

        self.cruds += [
            dict(c='inventory', f='unit_of_measure'),
            dict(c='inventory', f='system'),
            dict(c='inventory', f='subsystem'),
            dict(c='inventory', f='system_item'),
            dict(c='inventory', f='inventory_item'),
            ]
        return


    def create_defaults(self):
        tables = {}
        tables['unit_of_measure'] = self.default_unit_of_measure
        tables['system'] = self.default_system
        tables['subsystem'] = self.default_subsystem
        tables['system_item'] = self.default_sytem_item

        for k in tables:
            if db(db[k]).isempty():
                tables[k]()
        return


    def default_unit_of_measure(self):
        reader = csv_defaults('unit_of_measure.csv')
        if not reader:
            return

        defs = table_default_values(db.unit_of_measure)
        cols = Dict(acronym=0,name=1)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            defs['acronym'] = row[cols.acronym]
            defs['name'] = row[cols.name]

            db.unit_of_measure.update_or_insert(
                db.unit_of_measure.acronym==defs['acronym'], **defs)
        return

    def default_system(self):
        reader = csv_defaults('system.csv')
        if not reader:
            return

        defs = table_default_values(db.system)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            defs['name'] = row[0]

            db.system.update_or_insert(
                db.system.name==defs['name'], **defs)
        return

    def default_subsystem(self):
        reader = csv_defaults('subsystem.csv')
        if not reader:
            return

        defs = table_default_values(db.subsystem)
        cols = Dict(name=1,system=0)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            system = db(db.system.name == row[cols.system]).select().first()
            if not system:
                continue

            defs['system_id'] = system.id
            defs['name'] = row[cols.name]

            db.subsystem.update_or_insert(
                db.subsystem.system_id==defs['system_id'] and db.subsystem.name==defs['name'], **defs)
        return

    def default_sytem_item(self):
        reader = csv_defaults('system_item.csv')
        if not reader:
            return

        defs = table_default_values(db.system_item)
        cols = Dict(name=0,subsystem=1,unit=2,type=3)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            subsystem = db(db.subsystem.name == row[cols['subsystem']]).select().first()
            if not subsystem:
                continue
            unit = db(db.unit_of_measure.acronym == row[cols['unit']]).select().first()
            if not unit:
                continue

            defs['subsystem_id'] = subsystem.id
            defs['name'] = row[cols['name']]
            defs['item_type'] = row[cols['type']]
            defs['unit_of_measure_id'] = unit.id

            db.system_item.update_or_insert(
                db.system_item.item_type==defs['item_type'] and db.system_item.name==defs['name'], **defs)

    #--------------------------------------------------------------------------

    @staticmethod
    def unit_of_measure_represent(value, row):
        unit = db(db.unit_of_measure.id == row.unit_of_measure_id).select().first()
        return '%s %s' % (value, unit.acronym)

    @staticmethod
    def unit_of_measure_default():
        id = None
        unit = db(db.unit_of_measure.acronym == 'un').select().first()
        if unit:
            id = unit.id
        return id

    @staticmethod
    def km_unit_default():
        id = None
        unit = db(db.unit_of_measure.acronym == 'km').select().first()
        if unit:
            id = unit.id
        return id

    @staticmethod
    def item_IS_IN_DB(status=None, item_type=None):
        query = (db.inventory_item.id > 0)
        if item_type:
            query &= (db.inventory_item.item_type == item_type)
        if status:
            query &= db.inventory_item.status.contains(status, all=False)

        return IS_IN_DB(db(query), db.inventory_item, db.inventory_item._format)

    #--------------------------------------------------------------------------
    # BEGIN BUSINESS RULES

    @staticmethod
    def change_item_status(item_id, new_status, owner_table, owner_key, owner_link):
        db(db.inventory_item.id == item_id).update(status=new_status)

        old_usage = db((db.usage_history.item_id == item_id) \
            & (db.usage_history.usage_end == None)).select().first()
        if old_usage:
            old_usage.update_record(usage_end=request.now, status_end=new_status)

        if new_status != 'available':
            defs = table_default_values(db.usage_history)
            defs['item_id'] = item_id
            defs['owner_table'] = owner_table
            defs['owner_key'] = owner_key
            defs['owner_link'] = owner_link

            db.usage_history.insert(**defs)
        return

    @staticmethod
    def inventory_item_autocreate(count):
        tire = db(db.inventory_item.item_type == 'tire').select().first()
        for i in range(count):
            defs = table_default_values(db.inventory_item)
            defs['description'] = defs['number'].replace('I-', 'Pneu ')
            defs['item_type'] = tire.item_type
            defs['unit_of_measure_id'] = tire.unit_of_measure_id
            defs['status'] = tire.status
            defs['material_id'] = tire.material_id
            defs['initial_groove'] = tire.initial_groove
            defs['end_groove'] = tire.end_groove

            id = db.inventory_item.insert(**defs)
            TireControlModel.initial_groove(id)
        return

    # END BUSINESS RULES
    #--------------------------------------------------------------------------


