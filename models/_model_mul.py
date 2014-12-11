# -*- coding: utf-8 -*-

from onx_model import ModelBase
from h5_widgets import MaskWidget, H5EmailWidget, LookupWidget
from datetime import date, timedelta

class MULModel(ModelBase):
    name = 'mul'
    

    def define_tables(self):

        self.validate_required(db, ['platform', 'customer'])

        def _contract_key_compute(row):
            painel = db(db.painel.id > 0).select().first()
            days = (row.validate - painel.winning_factor).days

            factor = '{:0>4d}'.format(days)
            key = row.number+factor
            digit = module11_digit(key)
            return '%s-%s'% (key, digit)

        def _contract_key_repr(value, row):
            days = (row.validate - date.today()).days
            if days > 30:
                _class = 'success'
            elif days <= 0:
                _class = 'important'
            else:
                _class = 'warning'
            v = XML('<span class="label label-%s">%s</span>'% (_class, value))
            return v

        def _contract_validate_def():
            one_year = timedelta(days=365)
            validate = date.today() + one_year
            return validate

        db.define_table('mul_contract',
            #owner_fields,
            oplink_field,
            signature_fields,
            Field('number', 'string', label=T('Number')),
            Field('customer_id', db.customer, label=T('Customer')),
            Field('contract_date', 'date', label=T('Date')),
            Field('contact', 'string', label=T('Contact')),
            Field('phone', 'string', label=T('Phone')),
            Field('email', 'string', label=T('Email')),
            Field('note', 'text', label=T('Note')),
            Field('validate', 'date', label=T('Validate')),
            Field('licence_key', 'string', label=T('Key')),
            Field('is_active', 'boolean', label=T('Active')),
            migrate='mul_contract.table',
            format='%(number)s - %(validate)s')
        db.mul_contract.customer_id.requires = IS_IN_DB(db, db.customer, db.customer._format)
        db.mul_contract.customer_id.widget = LookupWidget().widget
        db.mul_contract.number.requires = [IS_NOT_EMPTY()]
        db.mul_contract.number.widget = MaskWidget(mask='000000').widget
        db.mul_contract.contract_date.default = request.now
        db.mul_contract.is_active.default = True
        db.mul_contract.is_active.represent = ONXREPR.repr_yes_no
        db.mul_contract.email.widget = H5EmailWidget().widget
        db.mul_contract.email.represent = ONXREPR.repr_mailto
        db.mul_contract.validate.default = _contract_validate_def
        db.mul_contract.licence_key.compute = _contract_key_compute
        db.mul_contract.licence_key.represent = _contract_key_repr
        db.mul_contract.updated_on.represent = ONXREPR.repr_updated_on_pretty
        db.mul_contract.updated_by.represent = ONXREPR.repr_updated_by
        db.mul_contract.note.represent = ONXREPR.repr_text


        db.define_table('mul_product',
            Field('code', 'string', label=T('Code')),
            Field('name', 'string', label=T('Name')),
            migrate='mul_product.table',
            format='[%(code)s] %(name)s')
        db.mul_product.code.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'mul_product.code')]        
        db.mul_product.code.widget = MaskWidget(mask='0000').widget
        db.mul_product.name.requires = [IS_NOT_EMPTY()]        
        

        def _contract_items_key_compute(row):
            painel = db(db.painel.id > 0).select().first()
            product = db(db.mul_product.id == row.product_id).select().first()
            days = (row.validate - painel.winning_factor).days
            number = db.mul_contract[row.contract_id].number[-4:]

            factor = '{:0>4d}'.format(days)
            key = product.code+number+factor
            digit = module11_digit(key)
            return '%s-%s'% (key, digit)

        def _contract_items_key_repr(value, row):
            from datetime import date
            days = (row.validate - date.today()).days
            if days > 10:
                _class = 'success'
            elif days <= 1:
                _class = 'important'
            else:
                _class = 'warning'
            v = XML('<span class="label label-%s">%s</span>'% (_class, value))
            return v

        def _contract_items_validate_def():
            validate = date.today() + timedelta(days=30)
            return validate

        db.define_table('mul_contract_items',
            #owner_fields,
            #oplink_field,
            signature_fields,
            Field('contract_id', db.mul_contract, label=T('Contract'), writable=False, readable=False),
            Field('product_id', db.mul_product, label=T('Product')),
            Field('is_active', 'boolean', label=T('Active')),
            Field('validate', 'date', label=T('Validate')),
            Field('licence_key', 'string', label=T('Key')),
            migrate='mul_contract_items.table',
            format='#%(id)s')
        db.mul_contract_items.contract_id.requires = IS_IN_DB(db, db.mul_contract, db.mul_contract._format)
        db.mul_contract_items.product_id.requires = IS_IN_DB(db, db.mul_product, db.mul_product._format)
        db.mul_contract_items.is_active.default = True
        db.mul_contract_items.is_active.represent = ONXREPR.repr_yes_no
        db.mul_contract_items.validate.default = _contract_items_validate_def
        db.mul_contract_items.licence_key.compute = _contract_items_key_compute
        db.mul_contract_items.licence_key.represent = _contract_items_key_repr


        db.define_table('mul_activation',
            Field('contract_id', db.mul_contract, label=T('Contract')),
            Field('activation_date', 'date', label=T('Date')),
            Field('log', 'text', label=T('Log')),
            migrate='mul_activation.table',
            format='#%(id)s')
        db.mul_activation.contract_id.requires = IS_IN_DB(db, db.mul_contract, db.mul_contract._format)
        db.mul_activation.activation_date.default = request.now
        

        '''

mul_contract
    customer
    number
    date
    active
    contact
    phone
    email
    server_name
    notes
    validate
    #attachments
    key - numero + fator vencimento + digito 1234561234X


mul_contract_items
    contract
    item
    active
    validate
    key


../app/mul/update()


/MUL --> management of user licenses
    /platform    --> exemplo onnix erp (onnix erp e onnix fiscal)
        #modules --> 02,04,08,16,32...
    /contract    --> contrato entre o cliente e a plataforma
        #modules --> modulos liberados no contrato
    /history     --> historico do contrato eas liberações
    
        '''
        return  
