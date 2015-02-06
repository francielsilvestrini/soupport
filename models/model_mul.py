# -*- coding: utf-8 -*-

from h5_widgets import MaskWidget, H5EmailWidget, LookupWidget
from datetime import date, timedelta

class MULModel(ModelBase):
    name = 'mul'


    def define_tables(self):

        self.validate_required(db, ['platform', 'person'])

        def _contract_key_compute(row):
            days = (row.validate - Settings.WINNING_FACTOR).days

            factor = '{0:>4d}'.format(days)
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
            Field('number', 'string', label=T('Number')),
            Field('customer_id', db.person, label=T('Customer')),
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
        db.mul_contract.customer_id.requires = IS_IN_DB(db(db.person.person_type.contains('customer')), db.person, db.person._format)
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
        self.cruds += [dict(c='mul', f='contract', t='mul_contract')]


        db.define_table('mul_product',
            Field('code', 'string', label=T('Code')),
            Field('name', 'string', label=T('Name')),
            Field('identifier', 'string', label=T('Identifier')),
            migrate='mul_product.table',
            format='[%(code)s] %(name)s')
        db.mul_product.code.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'mul_product.code')]
        db.mul_product.code.widget = MaskWidget(mask='0000').widget
        db.mul_product.name.requires = [IS_NOT_EMPTY()]
        db.mul_product.identifier.requires = [IS_NOT_EMPTY()]
        self.cruds += [dict(c='mul', f='product', t='mul_product')]


        def _contract_items_key_compute(row):
            painel = db(db.painel.id > 0).select().first()
            product = db(db.mul_product.id == row.product_id).select().first()
            days = (row.validate - Settings.WINNING_FACTOR).days
            number = db.mul_contract[row.contract_id].number[-4:]

            factor = '{0:>4d}'.format(days)
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
            Field('contract_id', db.mul_contract, label=T('Contract'), writable=False, readable=False),
            Field('product_id', db.mul_product, label=T('Product')),
            Field('is_active', 'boolean', label=T('Active')),
            Field('validate', 'date', label=T('Validate')),
            Field('licence_key', 'string', label=T('Key')),
            Field('max_rows', 'integer', label=T('Max. Rows')),
            migrate='mul_contract_items.table',
            format='#%(id)s')
        db.mul_contract_items.contract_id.requires = IS_IN_DB(db, db.mul_contract, db.mul_contract._format)
        db.mul_contract_items.product_id.requires = IS_IN_DB(db, db.mul_product, db.mul_product._format)
        db.mul_contract_items.is_active.default = True
        db.mul_contract_items.is_active.represent = ONXREPR.repr_yes_no
        db.mul_contract_items.validate.default = _contract_items_validate_def
        db.mul_contract_items.licence_key.compute = _contract_items_key_compute
        db.mul_contract_items.licence_key.represent = _contract_items_key_repr
        db.mul_contract_items.max_rows.default = 0
        self.set_table_defaults(db.mul_contract_items, 1, on_update_data=ModelBase.insert_default)


        db.define_table('mul_activation',
            Field('contract_id', db.mul_contract, label=T('Contract')),
            Field('activation_date', 'date', label=T('Date')),
            Field('log', 'text', label=T('Log')),
            migrate='mul_activation.table',
            format='#%(id)s')
        db.mul_activation.contract_id.requires = IS_IN_DB(db, db.mul_contract, db.mul_contract._format)
        db.mul_activation.activation_date.default = request.now
        return

    #--------------------------------------------------------------------------
    # BEGIN BUSINESS RULES

    @staticmethod
    def load_contract():
        try:
            registry = PainelModel.company().registry
            contract_id = request.application
            if contract_id == 'soupport':
                contract_id = '150002'

            if registry == Settings.ONNIX_REGISTRY:
                return None

            print registry, contract_id
            url = '%(host)s:%(port)s%(endpoint)s' % dict(
                host=Settings.LICENCE_HOSTNAME,
                port=Settings.LICENCE_HOSTPORT,
                endpoint=Settings.LICENCE_ENDPOINT)

            from xmlrpclib import ServerProxy
            server = ServerProxy(url)
            contract = server.contract(registry, contract_id)
            return contract
        except Exception, e:
            from onx_log import onx_logger
            onx_logger().error(str(e))
            return None


    # END BUSINESS RULES
    #--------------------------------------------------------------------------
