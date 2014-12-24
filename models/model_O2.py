# -*- coding: utf-8 -*-

from h5_widgets import LookupWidget

class O2Model(ModelBase):
    name = 'frota'

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
        'odometer_broken':T('Odometer Broken'),
        'odometer_reset':T('Odometer Reset'),
    }
    def define_tables(self):
        self.validate_required(db, ['O1_inventory_item'])


        db.define_table('O2_vehicle_type',
            Field('name', 'string', label=T('Name')),
            migrate='O2_vehicle_type.table',
            format='%(name)s')
        db.O2_vehicle_type.name.requires = [IS_NOT_EMPTY()]


        db.define_table('O2_vehicle',
            Field('licence_plate', 'string', label=T('License Plate')),
            Field('description', 'string', label=T('Description')),
            Field('vehicle_type_id', db.O2_vehicle_type, label=T('Type')),
            Field('is_active', 'boolean', label=T('Active')),

            Field('start_control', 'date', label=T('Start Control')),
            Field('odometer', 'double', label=T('Odometer')),
            
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

            Field('acquisition_date', 'date', label=T('Acquisition Date')),
            Field('acquisition_value', 'double', label=T('Acquisition Value')),
            Field('acquisition_dma', 'double', label=T('Depreciation Monthly Average (%)')),

            migrate='O2_vehicle.table',
            format='%(licence_plate)s - %(description)s')

        db.O2_vehicle.licence_plate.requires = [IS_UPPER(), 
                                                IS_NOT_EMPTY(), 
                                                IS_NOT_IN_DB(db, 'O2_vehicle.licence_plate')]
        db.O2_vehicle.description.requires = [IS_NOT_EMPTY()]
        db.O2_vehicle.vehicle_type_id.requires = IS_IN_DB(db, db.O2_vehicle_type, db.O2_vehicle_type._format)
        db.O2_vehicle.vehicle_type_id.widget = LookupWidget().widget
        db.O2_vehicle.is_active.default = True
        db.O2_vehicle.is_active.represent = ONXREPR.repr_yes_no
        db.O2_vehicle.start_control.default = request.now
        db.O2_vehicle.odometer.default = 0.0
        
        db.O2_vehicle.start_control.show_grid = False
        db.O2_vehicle.acquisition_date.show_grid = False
        db.O2_vehicle.acquisition_value.show_grid = False
        db.O2_vehicle.acquisition_dma.show_grid = False
        for f in filter(lambda f: 'bio_' in f.name,  db.O2_vehicle):
            f.show_grid = False


        db.define_table('O2_vehicle_status',
            Field('vehicle_id', db.O2_vehicle, label=T('Vehicle')),
            Field('status', 'string', label=T('Status')),
            Field('note', 'string', label=T('Note')),
            migrate='O2_vehicle_status.table',
            format=lambda row: O2Model.vehicle_status.get(row.status, row.status))
        db.O2_vehicle_status.vehicle_id.requires = IS_IN_DB(db, db.O2_vehicle, db.O2_vehicle._format)
        db.O2_vehicle_status.status.requires = IS_IN_SET(O2Model.vehicle_status)
        db.O2_vehicle_status.status.represent = lambda v,row: O2Model.vehicle_status.get(v, v)


        db.define_table('O2_vehicle_odometer',
            Field('vehicle_id', db.O2_vehicle, label=T('Vehicle')),
            Field('odometer_date', 'date', label=T('Date')),
            Field('status', 'string', label=T('Status')),
            Field('odometer', 'double', label=T('Odometer')),
            Field('note', 'string', label=T('Note')),
            owner_fields,
            migrate='O2_vehicle_odometer.table',
            format='%(odometer)s -> %(note)s')
        db.O2_vehicle_odometer.vehicle_id.requires = IS_IN_DB(db, db.O2_vehicle, db.O2_vehicle._format)
        db.O2_vehicle_odometer.odometer_date.default = request.now
        db.O2_vehicle_odometer.status.requires = IS_IN_SET(O2Model.vehicle_odometer_status)
        db.O2_vehicle_odometer.status.represent = lambda v,row: O2Model.vehicle_odometer_status.get(v, v)
        db.O2_vehicle_odometer.status.default = 'normal'
        db.O2_vehicle_odometer.odometer.default = 0.0


        def _vehicle_average_represent(value, row):
            type_average = O2Model.vehicle_type_average[row.type_average]
            return '%s %s' % (value, type_average)

        def _vehicle_fuel_format(row):
            fuel = field_rep(db.O2_vehicle_fuel.fuel_id, row.fuel_id, row)
            return fuel

        db.define_table('O2_vehicle_fuel',
            Field('vehicle_id', db.O2_vehicle, label=T('Vehicle')),
            Field('fuel_id', db.O1_system_item, label=T('Fuel')),
            Field('type_average', 'string', label=T('Type of Average')),
            Field('average_standard', 'double', label=T('Average Standard')),
            migrate='O2_vehicle_fuel.table',
            format=lambda row: _vehicle_fuel_format(row))
        db.O2_vehicle_fuel.vehicle_id.requires = IS_IN_DB(db, db.O2_vehicle, db.O2_vehicle._format)
        db.O2_vehicle_fuel.fuel_id.requires = IS_IN_DB(db(db.O1_system_item.item_type == 'fuel'), db.O1_system_item, db.O1_system_item._format)
        db.O2_vehicle_fuel.type_average.requires = IS_IN_SET(O2Model.vehicle_type_average)
        db.O2_vehicle_fuel.type_average.represent = lambda value, row: O2Model.vehicle_type_average[value]
        db.O2_vehicle_fuel.type_average.default = 'km_lt'
        db.O2_vehicle_fuel.average_standard.default = 0.0
        db.O2_vehicle_fuel.average_standard.represent = _vehicle_average_represent


        def _vehicle_refueling_distance_represent(value, row):
            return '%s km' % value

        def _vehicle_refueling_average_compute(row):
            average = round(row.distance / row.liters, 3)
            return average

        def _from_fuel_selected(row, field_name):
            fuel = db(db.O2_vehicle_fuel.id == row.fuel_id).select().first()
            value = fuel[field_name]
            return value

        db.define_table('O2_vehicle_refueling',
            Field('vehicle_id', db.O2_vehicle, label=T('Vehicle')),
            Field('fuel_id', db.O2_vehicle_fuel, label=T('Fuel')),
            Field('refueling_date', 'date', label=T('Date')),
            Field('old_odometer', 'double', label=T('Old Odometer')),
            Field('odometer', 'double', label=T('Odometer')),
            Field('distance', 'double', label=T('Distance')),
            Field('odometer_status', 'string', label=T('Odometer Status')),
            Field('liters', 'double', label=T('Liters')),
            Field('liter_price', 'double', label=T('Price per Liter')),
            Field('total_price', 'double', label=T('Total Price')),
            Field('average', 'double', label=T('Average')),
            Field('note', 'string', label=T('Note')),

            Field('type_average', 'string', label=T('Type of Average'), writable=False, readable=False),
            Field('average_standard', 'double', label=T('Average Standard'), writable=False, readable=False),
            Field('distance_standard', 'double', label=T('Distance Standard'), writable=False, readable=False),

            #Field('purchaser_id', 'integer', label=T('Purchaser')),
            #Field('invoice_reference', 'string', label=T('Invoice Reference')),
            #Field('supllier_id', 'integer', label=T('Supllier')),
            #Field('paid_in_advance', 'boolean', label=T('Paid in Advance')),#pode ser outro 
            migrate='O2_vehicle_refueling.table',
            format='%(id)s')
        db.O2_vehicle_refueling.vehicle_id.requires = IS_IN_DB(db, db.O2_vehicle, db.O2_vehicle._format)
        db.O2_vehicle_refueling.fuel_id.requires = IS_IN_DB(db, db.O2_vehicle_fuel, db.O2_vehicle_fuel._format)
        db.O2_vehicle_refueling.refueling_date.default = request.now
        db.O2_vehicle_refueling.old_odometer.default = 0.0
        db.O2_vehicle_refueling.odometer.requires = [IS_NOT_EMPTY()]
        db.O2_vehicle_refueling.odometer.default = 0.0
        db.O2_vehicle_refueling.odometer_status.requires = IS_IN_SET(O2Model.vehicle_odometer_status)
        db.O2_vehicle_refueling.odometer_status.represent = lambda v,row: O2Model.vehicle_odometer_status.get(v, v)
        db.O2_vehicle_refueling.odometer_status.default = 'normal'
        db.O2_vehicle_refueling.distance.requires = [IS_NOT_EMPTY()]
        db.O2_vehicle_refueling.distance.default = 0.0
        db.O2_vehicle_refueling.distance.represent = _vehicle_refueling_distance_represent

        db.O2_vehicle_refueling.liters.default = 0.0
        db.O2_vehicle_refueling.liter_price.default = 0.0
        db.O2_vehicle_refueling.total_price.default = 0.0
        db.O2_vehicle_refueling.average.compute = _vehicle_refueling_average_compute
        db.O2_vehicle_refueling.average.represent = _vehicle_average_represent

        db.O2_vehicle_refueling.type_average.requires = IS_IN_SET(O2Model.vehicle_type_average)
        db.O2_vehicle_refueling.type_average.represent = lambda value, row: O2Model.vehicle_type_average[value]
        db.O2_vehicle_refueling.type_average.compute = lambda row: _from_fuel_selected(row, 'type_average')
        db.O2_vehicle_refueling.average_standard.represent = _vehicle_average_represent
        db.O2_vehicle_refueling.average_standard.compute = lambda row: _from_fuel_selected(row, 'average_standard')
        db.O2_vehicle_refueling.distance_standard.represent = _vehicle_refueling_distance_represent
        db.O2_vehicle_refueling.distance_standard.compute = lambda row: row.average_standard * row.liters

        return  



    '''

pneu
    aplicacao/rodizio
    deposito
    reparo
    reforma
    desativacao
    apontamento de sulco
    suspensao de eixo

    
    comprador
    fatura ref
    fornecedor
    bandeira
    notas
    pago com adintamento
    >> apontamento de custo


    #veiculo_manutencao
    tipo da manutencao
    hodometro
    valor total
    data
    comprador
    fornecedor
    fatura ref
    >> manutencao realizada
        manutencao
        valor
        >> apontamento de garantia
    >> apontamento de custo


    #veiculo_viagem
    data
    situacao
    motivo
    >> receitas da viagem
        cliente
        data
        valor
        carga
        **tara, peso, capacidade % de ocupacao
        >>ratear custos
    >> adiantamento pode ser multiplos por viagem
        >> lancamentos
            data
            valor
            historico
        data_acerto
        saldo
        >> abastecimento
        >> despesas



    #veiculo_rodagem
    data_saida
    hodometro_saida
    motorista
    rota
    motivo
    data_entrada
    hodometro_entrada

layout
    nome:  truck 2 eixos
    eixo 1, dianteiro
        pneu 1, lado direito, pos 1
        pneu 2, lado esquerdo, pos 1
    eixo 2, traseiro
        pneu 3, lado direito, pos 1
        pneu 4, lado direito, pos 2
        pneu 5, lado esquerdo, pos 1
        pneu 6, lado esquerdo, pos 2


layout
    eixo
        dianteiro
            posicao
            






    '''

    def create_defaults(self):
        if db(db.O2_vehicle_type).isempty():
            types = ['Ciclomotor', 'Motoneta', 'Motocicleta', 'Triciclo', 'Automóvel', 
                     'Microônibus', 'Ônibus', 'Reboque', 'Semi-Reboque', 'Camioneta',
                     'Caminhão', 'Caminhão-Trator', 'Tr Rodas', 'Tr Esteiras', 'Tr Misto',
                     'Quadriciclo', 'Chassi Plataforma', 'Caminhonete', 'Utilitário', 
                     'Motor casa']
            defs = table_default_values(db.O2_vehicle_type)
            for t in types:
                defs['name'] = t
                db.O2_vehicle_type.update_or_insert(db.O2_vehicle_type.name==t, **defs)
        return


    #--------------------------------------------------------------------------

    @staticmethod
    def odometer_change(owner_table, owner_key, vehicle_id, odometer, odometer_status, note):
        defs = table_default_values(db.O2_vehicle_odometer)
        defs['owner_table'] = owner_table 
        defs['owner_key'] = owner_key
        defs['vehicle_id'] = vehicle_id
        defs['odometer'] = odometer
        defs['status'] = odometer_status
        defs['note'] = note
        
        db.O2_vehicle_odometer.insert(**defs)

        db(db.O2_vehicle.id == vehicle_id).update(odometer=odometer)
        return
        
    #--------------------------------------------------------------------------
        