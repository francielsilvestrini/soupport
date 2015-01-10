# -*- coding: utf-8 -*-

from h5_widgets import LookupWidget

class VehicleModel(ModelBase):
    name = 'vehicle'

    vehicle_status = {
        'at_home':T('At Home'),
        'maintenance':T('Maintenance'),
        'traveling':T('Traveling'),
        #baixado
        #
        }
    vehicle_status_color = {
        'at_home':'#468847',
        'maintenance':'#ff0000',
        'traveling':'#FFFF00',
        #baixado
        #
        }
    vehicle_type_average = {
        'km_lt':T('km/lt'),
        'hr_lt':T('hr/lt'),
    }

    vehicle_odometer_status = {
        'normal':T('Normal'),
        'odometer_reset':T('Odometer Reset'),
    }

    @staticmethod
    def vehicle_lookup(field, default):
        wgt = LookupWidget(
            add_new=lookup_url_new(c='fleet', f='vehicle')
            ).widget(field, default)
        return wgt

    @staticmethod
    def default_odometer(field, vehicle, default, start_range=0.0):
        field.default = default
        field.comment = T('Vehicle Odometer: %s %s') % (vehicle.current_odometer, \
            field_rep(db.vehicle.odometer_unit_id, vehicle.odometer_unit_id, vehicle))
        field.requires = IS_FLOAT_IN_RANGE(start_range, None)
        return field


    def define_tables(self):
        self.validate_required(db, ['inventory_item'])


        db.define_table('vehicle_type',
            Field('name', 'string', label=T('Name')),
            migrate='vehicle_type.table',
            format='%(name)s')
        db.vehicle_type.name.requires = [IS_NOT_EMPTY()]


        db.define_table('vehicle',
            Field('licence_plate', 'string', label=T('License Plate')),
            Field('description', 'string', label=T('Description')),
            Field('vehicle_type_id', db.vehicle_type, label=T('Type')),
            Field('reset_odometer', 'integer', label=T('Reset Odometer')),
            Field('current_odometer', 'double', label=T('Current Odometer')),
            Field('accumulated_odometer', 'double', label=T('Accumulated Odometer')),
            Field('odometer_unit_id', db.unit_of_measure, label=T('Unit of Odometer')),

            Field('bio_renavan', 'string', label=T('Renavan')),
            Field('bio_chassi', 'string', label=T('Chassi')),
            Field('bio_kind', 'string', label=T('Kind')),
            Field('bio_mark', 'string', label=T('Mark')),
            Field('bio_model', 'string', label=T('Model')),
            Field('bio_year', 'integer', label=T('Year of Manufacture')),
            Field('bio_year_model', 'integer', label=T('Year of Model')),
            Field('bio_color', 'string', label=T('Color')),
            Field('bio_doors', 'string', label=T('Doors')),
            Field('bio_transmission', 'string', label=T('Transmission')),
            Field('bio_horsepower', 'string', label=T('Horsepower')),
            Field('bio_co2emissions', 'double', label=T('CO2 Emissions')),

            #Field('acquisition_date', 'date', label=T('Acquisition Date')),
            #Field('acquisition_value', 'double', label=T('Acquisition Value')),
            #Field('acquisition_dma', 'double', label=T('Depreciation Monthly Average (%)')),
            Field('is_active', 'boolean', label=T('Active')),

            migrate='vehicle.table',
            format='%(licence_plate)s - %(description)s')

        db.vehicle.licence_plate.requires = [IS_UPPER(),
                                                IS_NOT_EMPTY(),
                                                IS_NOT_IN_DB(db, 'vehicle.licence_plate')]
        db.vehicle.description.requires = [IS_NOT_EMPTY()]
        db.vehicle.vehicle_type_id.requires = IS_IN_DB(db, db.vehicle_type, db.vehicle_type._format)
        db.vehicle.is_active.default = True
        db.vehicle.is_active.represent = ONXREPR.repr_yes_no
        db.vehicle.reset_odometer.default = 1
        db.vehicle.current_odometer.default = 0.0
        db.vehicle.odometer_unit_id.requires = IS_IN_DB(db, db.unit_of_measure, db.unit_of_measure._format)
        db.vehicle.odometer_unit_id.widget = InventoryModel.unit_of_measure_lookup
        db.vehicle.odometer_unit_id.default = InventoryModel.km_unit_default

        #db.vehicle.acquisition_date.show_grid = False
        #db.vehicle.acquisition_value.show_grid = False
        #db.vehicle.acquisition_dma.show_grid = False
        for f in filter(lambda f: 'bio_' in f.name,  db.vehicle):
            f.show_grid = False


        db.define_table('vehicle_status',
            Field('vehicle_id', db.vehicle, label=T('Vehicle')),
            Field('status', 'string', label=T('Status')),
            Field('note', 'string', label=T('Note')),
            migrate='vehicle_status.table',
            format=lambda row: VehicleModel.vehicle_status.get(row.status, row.status))
        db.vehicle_status.vehicle_id.requires = IS_IN_DB(db, db.vehicle, db.vehicle._format)
        db.vehicle_status.status.requires = IS_IN_SET(VehicleModel.vehicle_status)
        db.vehicle_status.status.represent = lambda v,row: VehicleModel.vehicle_status.get(v, v)


        def _from_vehicle(field_name, row):
            value = db.vehicle[row.vehicle_id][field_name]
            return value


        db.define_table('vehicle_odometer',
            Field('vehicle_id', db.vehicle, label=T('Vehicle')),
            Field('odometer_date', 'date', label=T('Date')),
            Field('status', 'string', label=T('Status'), writable=False),
            Field('reset', 'integer', label=T('Reset')),
            Field('odometer', 'double', label=T('Odometer')),
            Field('distance', 'double', label=T('Distance')),
            Field('note', 'string', label=T('Note')),
            Field('accumulated', 'double', label=T('Accumulated')),
            Field('unit_id', db.unit_of_measure, label=T('Unit of Odometer')),
            owner_fields,
            migrate='vehicle_odometer.table',
            format='%(id)s')
        db.vehicle_odometer.vehicle_id.requires = IS_IN_DB(db, db.vehicle, db.vehicle._format)
        db.vehicle_odometer.odometer_date.default = request.now
        db.vehicle_odometer.status.requires = IS_IN_SET(VehicleModel.vehicle_odometer_status)
        db.vehicle_odometer.status.represent = lambda v,row: VehicleModel.vehicle_odometer_status.get(v, v)
        db.vehicle_odometer.status.default = 'normal'
        db.vehicle_odometer.reset.compute = lambda row: _from_vehicle('reset_odometer', row)
        db.vehicle_odometer.odometer.default = 0.0
        db.vehicle_odometer.distance.default = 0.0
        db.vehicle_odometer.unit_id.requires = IS_IN_DB(db, db.unit_of_measure, db.unit_of_measure._format)
        db.vehicle_odometer.unit_id.widget = InventoryModel.unit_of_measure_lookup
        db.vehicle_odometer.unit_id.compute = lambda row: _from_vehicle('odometer_unit_id', row)


        def _vehicle_average_represent(value, row):
            type_average = VehicleModel.vehicle_type_average[row.type_average]
            return '%s %s' % (value, type_average)

        def _vehicle_fuel_format(row):
            fuel = field_rep(db.vehicle_fuel.fuel_id, row.fuel_id, row)
            return fuel

        db.define_table('vehicle_fuel',
            Field('vehicle_id', db.vehicle, label=T('Vehicle')),
            Field('fuel_id', db.system_item, label=T('Fuel')),
            Field('type_average', 'string', label=T('Type of Average')),
            Field('average_standard', 'double', label=T('Average Standard')),
            migrate='vehicle_fuel.table',
            format=lambda row: _vehicle_fuel_format(row))
        db.vehicle_fuel.vehicle_id.requires = IS_IN_DB(db, db.vehicle, db.vehicle._format)
        db.vehicle_fuel.fuel_id.requires = IS_IN_DB(db(db.system_item.item_type == 'fuel'), db.system_item, db.system_item._format)
        db.vehicle_fuel.fuel_id.width_lookup = '85%'
        db.vehicle_fuel.fuel_id.widget = InventoryModel.system_item_lookup
        db.vehicle_fuel.type_average.requires = IS_IN_SET(VehicleModel.vehicle_type_average)
        db.vehicle_fuel.type_average.represent = lambda value, row: VehicleModel.vehicle_type_average[value]
        db.vehicle_fuel.type_average.default = 'km_lt'
        db.vehicle_fuel.average_standard.default = 0.0
        db.vehicle_fuel.average_standard.represent = _vehicle_average_represent


        def _vehicle_refueling_average_compute(row):
            average = round(row.distance / row.liters, 3)
            return average

        def _from_fuel_selected(row, field_name):
            fuel = db(db.vehicle_fuel.id == row.fuel_id).select().first()
            value = fuel[field_name]
            return value

        db.define_table('vehicle_refueling',
            Field('vehicle_id', db.vehicle, label=T('Vehicle')),
            Field('fuel_id', db.vehicle_fuel, label=T('Fuel')),
            Field('refueling_date', 'date', label=T('Date')),
            Field('current_odometer', 'double', label=T('Odometer Current')),
            Field('liters', 'double', label=T('Liters')),
            Field('liter_price', 'double', label=T('Price per Liter')),
            Field('total_price', 'double', label=T('Total Price')),
            Field('note', 'string', label=T('Note')),

            Field('old_refueling', 'double', label=T('Old Refueling'), writable=False, readable=False),
            Field('current_refueling', 'double', label=T('Current Refueling'), writable=False, readable=False),
            Field('distance', 'double', label=T('Distance'), writable=False, readable=False),
            Field('average', 'double', label=T('Average'), writable=False, readable=False ),
            Field('type_average', 'string', label=T('Type of Average'), writable=False, readable=False),
            Field('average_standard', 'double', label=T('Average Standard'), writable=False, readable=False),
            Field('distance_standard', 'double', label=T('Distance Standard'), writable=False, readable=False),

            #Field('purchaser_id', 'integer', label=T('Purchaser')),
            #Field('invoice_reference', 'string', label=T('Invoice Reference')),
            #Field('supllier_id', 'integer', label=T('Supllier')),
            #Field('paid_in_advance', 'boolean', label=T('Paid in Advance')),#pode ser outro
            migrate='vehicle_refueling.table',
            format='%(id)s')
        db.vehicle_refueling.vehicle_id.requires = IS_IN_DB(db, db.vehicle, db.vehicle._format)
        db.vehicle_refueling.fuel_id.requires = IS_IN_DB(db, db.vehicle_fuel, db.vehicle_fuel._format)
        db.vehicle_refueling.refueling_date.default = request.now
        db.vehicle_refueling.current_odometer.requires = [IS_NOT_EMPTY()]
        db.vehicle_refueling.current_odometer.default = 0.0
        db.vehicle_refueling.liters.default = 0.0
        db.vehicle_refueling.liter_price.default = 0.0
        db.vehicle_refueling.total_price.default = 0.0

        db.vehicle_refueling.old_refueling.default = 0.0
        db.vehicle_refueling.current_refueling.default = 0.0
        db.vehicle_refueling.distance.default = 0.0

        db.vehicle_refueling.average.compute = _vehicle_refueling_average_compute
        db.vehicle_refueling.average.represent = _vehicle_average_represent

        db.vehicle_refueling.type_average.requires = IS_IN_SET(VehicleModel.vehicle_type_average)
        db.vehicle_refueling.type_average.represent = lambda value, row: VehicleModel.vehicle_type_average[value]
        db.vehicle_refueling.type_average.compute = lambda row: _from_fuel_selected(row, 'type_average')
        db.vehicle_refueling.average_standard.represent = _vehicle_average_represent
        db.vehicle_refueling.average_standard.compute = lambda row: _from_fuel_selected(row, 'average_standard')
        db.vehicle_refueling.distance_standard.compute = lambda row: row.average_standard * row.liters

        return


    def create_defaults(self):
        tables = {}
        tables['vehicle_type'] = self.default_vehicle_type
        for k in tables:
            if db(db[k]).isempty():
                tables[k]()
        return


    def default_vehicle_type(self):
        reader = csv_defaults('vehicle_type.csv')
        if not reader:
            return

        defs = table_default_values(db.vehicle_type)
        cols = Dict(name=0)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            defs['name'] = row[cols.name]

            db.vehicle_type.update_or_insert(
                db.vehicle_type.name==defs['name'], **defs)
        return

    #--------------------------------------------------------------------------
    # BEGIN BUSINESS RULES

    @staticmethod
    def vehicle_status_change(vehicle_id, new_status, note):
        defs = table_default_values(db.vehicle_status)
        defs['vehicle_id'] = vehicle_id
        defs['status'] = new_status
        defs['note'] = note
        db.vehicle_status.insert(**defs)
        return


    @staticmethod
    def vehicle_odometer_change(vehicle_id, odometer_status, odometer, note, owner_table, owner_key, owner_link):
        vehicle = db.vehicle[vehicle_id]

        if odometer_status == 'odometer_reset':
            reset = vehicle.reset_odometer + 1
            odometer = 0.0
            distance = 0.0
            accumulated = vehicle.accumulated_odometer
        elif odometer > vehicle.current_odometer:
            reset = vehicle.reset_odometer
            distance = odometer - vehicle.current_odometer
            accumulated = vehicle.accumulated_odometer + distance
        else:
            reset = vehicle.reset_odometer
            distance = vehicle.accumulated_odometer if owner_table == 'vehicle' else 0.0
            accumulated = vehicle.accumulated_odometer

        defs = table_default_values(db.vehicle_odometer)
        defs['vehicle_id'] = vehicle_id
        defs['status'] = odometer_status
        defs['odometer'] = odometer
        defs['distance'] = distance
        defs['accumulated'] = accumulated
        defs['note'] = note
        defs['owner_table'] = owner_table
        defs['owner_key'] = owner_key
        defs['owner_link'] = owner_link
        db.vehicle_odometer.insert(**defs)

        if owner_table != 'vehicle' and (odometer > vehicle.current_odometer or odometer_status == 'odometer_reset'):
            vehicle.update_record(reset_odometer=reset, current_odometer=odometer, accumulated_odometer=accumulated)
        return dict(accumulated=accumulated)

    # END BUSINESS RULES
    #--------------------------------------------------------------------------
