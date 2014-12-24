# -*- coding: utf-8 -*-

from onx_files import csv_defaults

class O1Model(ModelBase):
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


    def define_tables(self):
        #self.validate_required(db, ['platform', 'customer'])


        db.define_table('O1_unit_of_measure',
            Field('acronym', 'string', label=T('Acronym')),
            Field('name', 'string', label=T('Name')),
            migrate='O1_unit_of_measure.table',
            format='%(acronym)s - %(name)s')
        db.O1_unit_of_measure.acronym.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'O1_unit_of_measure.acronym')]
        db.O1_unit_of_measure.name.requires = [IS_NOT_EMPTY()]


        db.define_table('O1_system',
            Field('name', 'string', label=T('Name')),
            migrate='O1_system.table',
            format='%(name)s')
        db.O1_system.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'O1_system.name')]


        def _subsystem_format(row):
            system = field_rep(db.O1_subsystem.system_id, row.system_id, row)
            return '%s/%s' % (system, row.name)

        db.define_table('O1_subsystem',
            Field('system_id', db.O1_system, label=T('System')),
            Field('name', 'string', label=T('Name')),
            migrate='O1_subsystem.table',
            format=lambda row:_subsystem_format(row))
        db.O1_subsystem.system_id.requires = IS_IN_DB(db, db.O1_system, db.O1_system._format)
        db.O1_subsystem.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'O1_subsystem.name')]


        db.define_table('O1_system_item',
            Field('subsystem_id', db.O1_subsystem, label=T('Subsystem')),
            Field('name', 'string', label=T('Name')),
            Field('item_type', 'string', label=T('Type')),
            Field('unit_of_measure_id', db.O1_unit_of_measure, label=T('Unit of Measure')),
            Field('is_active', 'boolean', label=T('Active')),
            migrate='O1_system_item.table',
            format='%(name)s')
        db.O1_system_item.subsystem_id.requires = IS_IN_DB(db, db.O1_subsystem, db.O1_subsystem._format)
        db.O1_system_item.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'O1_system_item.name')]
        db.O1_system_item.item_type.requires = IS_IN_SET(O1Model.system_item_type)
        db.O1_system_item.item_type.represent = lambda value, row: O1Model.system_item_type[value]
        db.O1_system_item.unit_of_measure_id.requires = IS_IN_DB(db, db.O1_unit_of_measure, db.O1_unit_of_measure._format)
        db.O1_system_item.is_active.default = True


        db.define_table('O1_inventory_item',
            Field('number', 'string', label=T('Number')),
            Field('description', 'string', label=T('Description')),
            Field('item_type', 'string', label=T('Type')),
            Field('unit_of_measure_id', db.O1_unit_of_measure, label=T('Unit of Measure')),
            Field('status', 'string', label=T('Status')),
            Field('material_id', db.O1_system_item, label=T('Material')),
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
            migrate='O1_inventory_item.table',
            format='%(number)s - %(description)s')
        db.O1_inventory_item.number.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'O1_inventory_item.number')]
        db.O1_inventory_item.number.default = lambda: CommomModel.sequence_ticket('O1_inventory_item', 'I-')
        db.O1_inventory_item.description.requires = [IS_NOT_EMPTY()]
        db.O1_inventory_item.item_type.requires = IS_IN_SET(O1Model.inventory_item_type)
        db.O1_inventory_item.item_type.represent = lambda value, row: O1Model.inventory_item_type.get(value, value)
        db.O1_inventory_item.unit_of_measure_id.requires = IS_IN_DB(db, db.O1_unit_of_measure, db.O1_unit_of_measure._format)
        db.O1_inventory_item.unit_of_measure_id.default = O1Model.unit_of_measure_default
        db.O1_inventory_item.status.requires = IS_IN_SET(O1Model.inventory_item_status)
        db.O1_inventory_item.status.represent = lambda value, row: O1Model.inventory_item_status.get(value, value)
        db.O1_inventory_item.status.default = 'available'
        db.O1_inventory_item.material_id.requires = IS_IN_DB(db(db.O1_system_item.item_type == 'material'), db.O1_system_item, db.O1_system_item._format)
        db.O1_inventory_item.material_id.widget = LookupWidget().widget        
        db.O1_inventory_item.initial_groove.default = 10.0
        db.O1_inventory_item.initial_groove.show_grid = False
        db.O1_inventory_item.end_groove.default = 1.0
        db.O1_inventory_item.end_groove.show_grid = False


        db.define_table('O1_usage_history',
            Field('item_id', db.O1_inventory_item, label=T('Item')),
            Field('usage_start', 'datetime', label=T('Start')),
            Field('usage_end', 'datetime', label=T('End')),
            Field('status_end', 'string', label=T('Status End')),
            owner_fields,
            migrate='O1_usage_history.table',
            format='%(id)s')
        db.O1_usage_history.item_id.requires = IS_IN_DB(db, db.O1_inventory_item, db.O1_inventory_item._format)
        db.O1_usage_history.usage_start.default = request.now
        db.O1_usage_history.status_end.requires = IS_IN_SET(O1Model.inventory_item_status)
        db.O1_usage_history.status_end.represent = lambda value, row: O1Model.inventory_item_status.get(value, value or '')


        db.define_table('O1_component_item',
            owner_fields,
            Field('component_id', db.O1_inventory_item, label=T('Component')),
            migrate='O1_component_item.table',
            format='%(id)s')
        db.O1_component_item.component_id.requires = IS_IN_DB(db(db.O1_inventory_item.item_type == 'component'), db.O1_inventory_item, db.O1_inventory_item._format)
        db.O1_component_item.component_id.widget = LookupWidget(width='90%').widget

        
        return  


    def create_defaults(self):
        tables = {}
        tables['O1_unit_of_measure'] = self.default_unit_of_measure
        tables['O1_system'] = self.default_system
        tables['O1_subsystem'] = self.default_subsystem
        tables['O1_system_item'] = self.default_sytem_item

        for k in tables:
            if db(db[k]).isempty():
                tables[k]()
        return


    def default_unit_of_measure(self):
        reader = csv_defaults('O1_unit_of_measure.csv')
        if not reader:
            return
            
        defs = table_default_values(db.O1_unit_of_measure)
        cols = Dict(acronym=0,name=1)
        for i, row in enumerate(reader):
            if i == 0: 
                continue
            defs['acronym'] = row[cols.acronym]
            defs['name'] = row[cols.name]

            db.O1_unit_of_measure.update_or_insert(
                db.O1_unit_of_measure.acronym==defs['acronym'], **defs)        
        return

    def default_system(self):
        reader = csv_defaults('O1_system.csv')
        if not reader:
            return
            
        defs = table_default_values(db.O1_system)
        for i, row in enumerate(reader):
            if i == 0: 
                continue
            defs['name'] = row[0]

            db.O1_system.update_or_insert(
                db.O1_system.name==defs['name'], **defs)        
        return

    def default_subsystem(self):
        reader = csv_defaults('O1_subsystem.csv')
        if not reader:
            return
            
        defs = table_default_values(db.O1_subsystem)
        cols = Dict(name=1,system=0)
        for i, row in enumerate(reader):
            if i == 0: 
                continue
            system = db(db.O1_system.name == row[cols.system]).select().first() 
            if not system: 
                continue

            defs['system_id'] = system.id
            defs['name'] = row[cols.name]

            db.O1_subsystem.update_or_insert(
                db.O1_subsystem.system_id==defs['system_id'] and db.O1_subsystem.name==defs['name'], **defs)
        return                

    def default_sytem_item(self):
        reader = csv_defaults('O1_system_item.csv')
        if not reader:
            return
            
        defs = table_default_values(db.O1_system_item)
        cols = Dict(name=0,subsystem=1,unit=2,type=3)
        for i, row in enumerate(reader):
            if i == 0: 
                continue
            subsystem = db(db.O1_subsystem.name == row[cols['subsystem']]).select().first() 
            if not subsystem: 
                continue
            unit = db(db.O1_unit_of_measure.acronym == row[cols['unit']]).select().first() 
            if not unit: 
                continue

            defs['subsystem_id'] = subsystem.id
            defs['name'] = row[cols['name']]
            defs['item_type'] = row[cols['type']]
            defs['unit_of_measure_id'] = unit.id

            db.O1_system_item.update_or_insert(
                db.O1_system_item.item_type==defs['item_type'] and db.O1_system_item.name==defs['name'], **defs)

    #--------------------------------------------------------------------------

    @staticmethod
    def unit_of_measure_represent(value, row):
        unit = db(db.O1_unit_of_measure.id == row.unit_of_measure_id).select().first()            
        return '%s %s' % (value, unit.acronym)

    @staticmethod
    def unit_of_measure_default():
        id = None
        unit = db(db.O1_unit_of_measure.acronym == 'un').select().first()
        if unit:
            id = unit.id
        return id

    #--------------------------------------------------------------------------
    # BEGIN BUSINESS RULES

    @staticmethod
    def change_item_status(item_id, new_status, owner_table, owner_key, owner_link):
        db(db.O1_inventory_item.id == item_id).update(status=new_status)

        old_usage = db((db.O1_usage_history.item_id == item_id) \
            & (db.O1_usage_history.usage_end == None)).select().first()
        if old_usage:
            old_usage.update_record(usage_end=request.now, status_end=new_status)

        if new_status != 'available':
            defs = table_default_values(db.O1_usage_history)
            defs['item_id'] = item_id
            defs['owner_table'] = owner_table
            defs['owner_key'] = owner_key
            defs['owner_link'] = owner_link

            db.O1_usage_history.insert(**defs)
        return

    # END BUSINESS RULES
    #--------------------------------------------------------------------------


