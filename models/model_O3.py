# -*- coding: utf-8 -*-

class O3Model(ModelBase):

    name = 'tire_control'

    def __init__(self):
        ModelBase.__init__(self)
        self.crud_controller = 'tire_control'
        self.crud_start = 3
        return

    axle_wheel_side = {
        'left':T('Left'), 
        'right':T('Right'), 
    }

    chassi_axle_position = {
        'front':T('Front'), 
        'rear':T('Rear'), 
        'steppe':T('Steppe'), 
    }

    def define_tables(self):
        self.validate_required(db, ['O2_vehicle'])

        self.cruds += ['O3_axle']
        db.define_table('O3_axle',
            Field('name', 'string', label=T('Name')),
            migrate='O3_axle.table',
            format='%(name)s')
        db.O3_axle.name.requires = [IS_NOT_EMPTY()]


        db.define_table('O3_axle_wheel',
            Field('axle_id', db.O3_axle, label=T('Axle')),
            Field('side', 'string', label=T('Side')),
            Field('position', 'integer', label=T('Position')),
            migrate='O3_axle_wheel.table',
            format='%(id)s')
        db.O3_axle_wheel.axle_id.requires = IS_IN_DB(db, db.O3_axle, db.O3_axle._format)
        db.O3_axle_wheel.side.requires = IS_IN_SET(O3Model.axle_wheel_side)
        db.O3_axle_wheel.side.represent = lambda value, row: O3Model.axle_wheel_side[value]
        db.O3_axle_wheel.position.default = 1


        self.cruds += ['O3_chassi']
        db.define_table('O3_chassi',
            Field('name', 'string', label=T('Name')),
            migrate='O3_chassi.table',
            format='%(name)s')
        db.O3_chassi.name.requires = [IS_NOT_EMPTY()]

        db.define_table('O3_chassi_axle',
            Field('chassi_id', db.O3_chassi, label=T('Chassi')),
            Field('axle_id', db.O3_axle, label=T('Axle')),
            Field('position', 'string', label=T('Position')),
            Field('sequence', 'integer', label=T('Sequence')),
            migrate='O3_chassi_axle.table',
            format='%(id)s')
        db.O3_chassi_axle.chassi_id.requires = IS_IN_DB(db, db.O3_chassi, db.O3_chassi._format)
        db.O3_chassi_axle.axle_id.requires = IS_IN_DB(db, db.O3_axle, db.O3_axle._format)
        db.O3_chassi_axle.position.requires = IS_IN_SET(O3Model.chassi_axle_position)
        db.O3_chassi_axle.position.represent = lambda value, row: O3Model.chassi_axle_position.get(value) or value
        db.O3_chassi_axle.sequence.default = 1


        db.define_table('O3_tire_control',
            Field('vehicle_id', db.O2_vehicle, label=T('Vehicle')),
            Field('chassi_id', db.O3_chassi, label=T('Chassi')),
            migrate='O3_tire_control.table',
            format='%(id)s')
        db.O3_tire_control.vehicle_id.requires = IS_IN_DB(db, db.O2_vehicle, db.O2_vehicle._format)
        db.O3_tire_control.chassi_id.requires = IS_IN_DB(db, db.O3_chassi, db.O3_chassi._format)


        db.define_table('O3_tire_control_item',
            Field('tire_control_id', db.O3_tire_control, label=T('Tire Control')),
            Field('axle_position', 'string', label=T('Axle Position')),
            Field('axle_sequence', 'integer', label=T('Axle Sequence')),
            Field('wheel_side', 'string', label=T('Wheel Side')),
            Field('wheel_position', 'integer', label=T('Wheel Position')),
            Field('tire_id', db.O1_inventory_item, label=T('Tire')),
            Field('odometer', 'double', label=T('Odometer')),
            migrate='O3_tire_control_item.table',
            format='%(id)s')
        db.O3_tire_control_item.tire_control_id.requires = IS_IN_DB(db, db.O3_tire_control, db.O3_tire_control._format)
        db.O3_tire_control_item.axle_position.requires = IS_IN_SET(O3Model.chassi_axle_position)
        db.O3_tire_control_item.axle_position.represent = lambda value, row: O3Model.chassi_axle_position.get(value) or value
        db.O3_tire_control_item.wheel_side.requires = IS_IN_SET(O3Model.axle_wheel_side)
        db.O3_tire_control_item.wheel_side.represent = lambda value, row: O3Model.axle_wheel_side[value]
        db.O3_tire_control_item.tire_id.requires = IS_IN_DB(db(db.O1_inventory_item.item_type == 'tire'), db.O1_inventory_item, db.O1_inventory_item._format)
        db.O3_tire_control_item.tire_id.widget = LookupWidget().widget
        db.O3_tire_control_item.odometer.default = 0.0

      
        db.define_table('O3_groove_annotation',
            Field('tire_id', db.O1_inventory_item, label=T('Tire')),
            Field('annotation_date', 'date', label=T('Date')),
            Field('groove', 'double', label=T('Groove')),
            Field('vehicle_id', db.O2_vehicle, label=T('Vehicle')),
            Field('old_odometer', 'double', label=T('Old Odometer')),
            Field('odometer', 'double', label=T('Odometer')),
            Field('distance', 'double', label=T('Distance')),
            Field('note', 'string', label=T('Note')),
            migrate='O3_groove_annotation.table',
            format='%(id)s')
        db.O3_groove_annotation.tire_id.requires = IS_IN_DB(db(db.O1_inventory_item.item_type == 'tire'), db.O1_inventory_item, db.O1_inventory_item._format)
        db.O3_groove_annotation.annotation_date.default = request.now
        db.O3_groove_annotation.groove.default = 0.0
        db.O3_groove_annotation.vehicle_id.requires = IS_IN_DB(db, db.O2_vehicle, db.O2_vehicle._format)
        db.O3_groove_annotation.vehicle_id.widget = LookupWidget().widget
        db.O3_groove_annotation.old_odometer.default = 0.0
        db.O3_groove_annotation.odometer.default = 0.0
        db.O3_groove_annotation.distance.default = 0.0
        
        return  

    def create_defaults(self):
        return


    #--------------------------------------------------------------------------
    # BEGIN BUSINESS RULES

    @staticmethod
    def change_chassi(tc_id):

        def find_old_tire(old_items, axle_position, axle_sequence, wheel_side, wheel_position):
            tire_id = None
            for item in old_items:
                if (item.axle_position == axle_position) \
                and (item.axle_sequence == axle_sequence) \
                and (item.wheel_side == wheel_side) \
                and (item.wheel_position == wheel_position):
                    tire_id = item.tire_id
                    break
            return tire_id


        old_items = db((db.O3_tire_control_item.tire_control_id == tc_id) & (db.O3_tire_control_item.tire_id != None)).select()

        #delete all old items
        db(db.O3_tire_control_item.tire_control_id == tc_id).delete()

        #change tire status avaliable
        for item in old_items:
            O1Model.change_item_status(item.tire_id, 'available')

        #include new items
        chassi_id = db.O3_tire_control[tc_id].chassi_id
        chassi_axles = db(db.O3_chassi_axle.chassi_id == chassi_id).select(
            orderby=db.O3_chassi_axle.position|db.O3_chassi_axle.sequence)

        for axle in chassi_axles:
            axle_wheels = db(db.O3_axle_wheel.axle_id == axle.axle_id).select(
                orderby=db.O3_axle_wheel.side|db.O3_axle_wheel.position)
            for wheel in axle_wheels:
                tc_item = table_default_values(db.O3_tire_control_item)
                tc_item['tire_control_id'] = tc_id
                tc_item['axle_position'] = axle.position
                tc_item['axle_sequence'] = axle.sequence
                tc_item['wheel_side'] = wheel.side
                tc_item['wheel_position'] = wheel.position
                tc_item['tire_id'] = find_old_tire(old_items, 
                    axle.position, axle.sequence, wheel.side, wheel.position)
                db.O3_tire_control_item.insert(**tc_item)
                if tc_item['tire_id']:
                    O1Model.change_item_status(tc_item['tire_id'], 'in_use')

        return

    @staticmethod
    def initial_groove(item_id):
        item = db(db.O1_inventory_item.id == item_id).select().first()
        
        defs = table_default_values(db.O3_groove_annotation)
        defs['tire_id'] = item_id
        defs['groove'] = item.initial_groove
        defs['note'] = T('Initial Groove')
        db.O3_groove_annotation.insert(**defs)             
        return
        
    # END BUSINESS RULES
    #--------------------------------------------------------------------------
