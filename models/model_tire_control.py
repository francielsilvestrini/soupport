# -*- coding: utf-8 -*-

class TireControlModel(ModelBase):

    name = 'tire_control'

    def __init__(self):
        ModelBase.__init__(self)
        self.crud_controller = 'tire_control'
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

    @staticmethod
    def axle_lookup(field, default):
        wgt = LookupWidget(
            add_new=lookup_url_new(c='tire_control', f='axle')
            ).widget(field, default)
        return wgt

    @staticmethod
    def chassi_lookup(field, default):
        wgt = LookupWidget(
            add_new=lookup_url_new(c='tire_control', f='chassi')
            ).widget(field, default)
        return wgt

    def define_tables(self):
        self.validate_required(db, ['vehicle'])

        db.define_table('axle',
            Field('name', 'string', label=T('Name')),
            migrate='axle.table',
            format='%(name)s')
        db.axle.name.requires = [IS_NOT_EMPTY()]
        self.cruds += [dict(c='tire_control', f='axle')]


        db.define_table('axle_wheel',
            Field('axle_id', db.axle, label=T('Axle')),
            Field('side', 'string', label=T('Side')),
            Field('position', 'integer', label=T('Position')),
            migrate='axle_wheel.table',
            format='%(id)s')
        db.axle_wheel.axle_id.requires = IS_IN_DB(db, db.axle, db.axle._format)
        db.axle_wheel.side.requires = IS_IN_SET(TireControlModel.axle_wheel_side)
        db.axle_wheel.side.represent = lambda value, row: TireControlModel.axle_wheel_side[value]
        db.axle_wheel.position.default = 1


        db.define_table('chassi',
            Field('name', 'string', label=T('Name')),
            migrate='chassi.table',
            format='%(name)s')
        db.chassi.name.requires = [IS_NOT_EMPTY()]
        self.cruds += [dict(c='tire_control', f='chassi')]


        db.define_table('chassi_axle',
            Field('chassi_id', db.chassi, label=T('Chassi')),
            Field('axle_id', db.axle, label=T('Axle')),
            Field('position', 'string', label=T('Position')),
            Field('sequence', 'integer', label=T('Sequence')),
            migrate='chassi_axle.table',
            format='%(id)s')
        db.chassi_axle.chassi_id.requires = IS_IN_DB(db, db.chassi, db.chassi._format)
        db.chassi_axle.axle_id.requires = IS_IN_DB(db, db.axle, db.axle._format)
        db.chassi_axle.position.requires = IS_IN_SET(TireControlModel.chassi_axle_position)
        db.chassi_axle.position.represent = lambda value, row: TireControlModel.chassi_axle_position.get(value) or value
        db.chassi_axle.sequence.default = 1


        db.define_table('tire_control',
            Field('vehicle_id', db.vehicle, label=T('Vehicle')),
            Field('chassi_id', db.chassi, label=T('Chassi')),
            migrate='tire_control.table',
            format='%(id)s')
        db.tire_control.vehicle_id.requires = IS_IN_DB(db, db.vehicle, db.vehicle._format)
        db.tire_control.chassi_id.requires = IS_IN_DB(db, db.chassi, db.chassi._format)
        db.tire_control.chassi_id.widget = TireControlModel.chassi_lookup


        def _tc_item_distance(row):
            try:
                item = row.tire_control_item
                distance = db.vehicle[item.vehicle_id].accumulated_odometer - item.start_control
                distance = distance if distance >= 0.0 else 0.0
                return distance
            except Exception, e:
                return str(e)

        def _tc_item_full_distance(row):
            try:
                item = row.tire_control_item
                full_distance = _tc_item_distance(row) + db.inventory_item[item.tire_id].use_count
                return full_distance
            except Exception, e:
                return str(e)

        db.define_table('tire_control_item',
            Field('vehicle_id', db.vehicle, label=T('Vehicle')),
            Field('tire_control_id', db.tire_control, label=T('Tire Control')),
            Field('axle_position', 'string', label=T('Axle Position')),
            Field('axle_sequence', 'integer', label=T('Axle Sequence')),
            Field('wheel_side', 'string', label=T('Wheel Side')),
            Field('wheel_position', 'integer', label=T('Wheel Position')),
            Field('start_date', 'date', label=T('Start Date')),
            Field('tire_id', db.inventory_item, label=T('Tire')),
            Field('start_odometer', 'double', label=T('Start Odometer')),
            Field('start_control', 'double', label=T('Start Control'), writable=False, readable=False),
            Field.Virtual('distance', lambda row: _tc_item_distance(row), label=T('Distance')),
            Field.Virtual('full_distance', lambda row: _tc_item_full_distance(row), label=T('Full Distance')),
            migrate='tire_control_item.table',
            format='%(id)s')
        db.tire_control_item.vehicle_id.requires = IS_IN_DB(db, db.vehicle, db.vehicle._format)
        db.tire_control_item.tire_control_id.requires = IS_IN_DB(db, db.tire_control, db.tire_control._format)
        db.tire_control_item.axle_position.requires = IS_IN_SET(TireControlModel.chassi_axle_position)
        db.tire_control_item.axle_position.represent = lambda value, row: TireControlModel.chassi_axle_position.get(value) or value
        db.tire_control_item.wheel_side.requires = IS_IN_SET(TireControlModel.axle_wheel_side)
        db.tire_control_item.wheel_side.represent = lambda value, row: TireControlModel.axle_wheel_side[value]
        db.tire_control_item.tire_id.requires = IS_IN_DB(db(db.inventory_item.item_type == 'tire'), db.inventory_item, db.inventory_item._format)
        db.tire_control_item.tire_id.widget = InventoryModel.inventory_item_lookup
        db.tire_control_item.start_date.default = request.now
        db.tire_control_item.start_odometer.default = 0.0
        db.tire_control_item.start_control.default = 0.0


        db.define_table('groove_annotation',
            Field('tire_id', db.inventory_item, label=T('Tire')),
            Field('annotation_date', 'date', label=T('Date')),
            Field('groove', 'double', label=T('Groove')),
            Field('vehicle_id', db.vehicle, label=T('Vehicle')),
            Field('old_odometer', 'double', label=T('Old Odometer')),
            Field('odometer', 'double', label=T('Odometer')),
            Field('distance', 'double', label=T('Distance')),
            Field('note', 'string', label=T('Note')),
            migrate='groove_annotation.table',
            format='%(id)s')
        db.groove_annotation.tire_id.requires = IS_IN_DB(db(db.inventory_item.item_type == 'tire'), db.inventory_item, db.inventory_item._format)
        db.groove_annotation.annotation_date.default = request.now
        db.groove_annotation.groove.default = 0.0
        db.groove_annotation.vehicle_id.requires = IS_IN_DB(db, db.vehicle, db.vehicle._format)
        db.groove_annotation.vehicle_id.widget = VehicleModel.vehicle_lookup
        db.groove_annotation.old_odometer.default = 0.0
        db.groove_annotation.odometer.default = 0.0
        db.groove_annotation.distance.default = 0.0

        return

    def create_defaults(self):
        return


    #--------------------------------------------------------------------------
    # BEGIN BUSINESS RULES

    @staticmethod
    def change_chassi(tc_id):

        def find_old_tire(old_items, axle_position, axle_sequence, wheel_side, wheel_position):
            old_item = None
            for item in old_items:
                if (item.axle_position == axle_position) \
                and (item.axle_sequence == axle_sequence) \
                and (item.wheel_side == wheel_side) \
                and (item.wheel_position == wheel_position):
                    old_item = item
                    break
            return old_item


        old_items = db((db.tire_control_item.tire_control_id == tc_id) & (db.tire_control_item.tire_id != None)).select()

        #delete all old items
        db(db.tire_control_item.tire_control_id == tc_id).delete()

        #change tire status avaliable
        for item in old_items:
            InventoryModel.change_item_status(item.tire_id, 'available')

        #include new items
        tc = db.tire_control[tc_id]
        chassi_axles = db(db.chassi_axle.chassi_id == tc.chassi_id).select(
            orderby=db.chassi_axle.position|db.chassi_axle.sequence)

        for axle in chassi_axles:
            axle_wheels = db(db.axle_wheel.axle_id == axle.axle_id).select(
                orderby=db.axle_wheel.side|db.axle_wheel.position)
            for wheel in axle_wheels:
                tc_item = table_default_values(db.tire_control_item)
                tc_item['tire_control_id'] = tc_id
                tc_item['vehicle_id'] = tc.vehicle_id
                tc_item['axle_position'] = axle.position
                tc_item['axle_sequence'] = axle.sequence
                tc_item['wheel_side'] = wheel.side
                tc_item['wheel_position'] = wheel.position
                old_item = find_old_tire(old_items, axle.position, axle.sequence, wheel.side, wheel.position)
                if old_item:
                    tc_item['tire_id'] = old_item.tire_id
                    tc_item['start_date'] = old_item.start_date
                    tc_item['start_odometer'] = old_item.start_odometer
                    tc_item['start_control'] = old_item.start_control
                db.tire_control_item.insert(**tc_item)
                if tc_item.get('tire_id'):
                    InventoryModel.change_item_status(tc_item['tire_id'], 'in_use')
        return

    @staticmethod
    def initial_groove(item_id):
        item = db(db.inventory_item.id == item_id).select().first()

        defs = table_default_values(db.groove_annotation)
        defs['tire_id'] = item_id
        defs['groove'] = item.initial_groove
        defs['note'] = T('Initial Groove')
        db.groove_annotation.insert(**defs)
        return

    # END BUSINESS RULES
    #--------------------------------------------------------------------------
