# -*- coding: utf-8 -*-

from h5_widgets import MultipleWidget

class EntriesModel(ModelBase):
    name = 'entries'

    person_type = {
        'customer':T('Customer'),
        'supplier':T('Supplier'),
        }

    @staticmethod
    def person_type_selects(field, default, **attr):
        wgt = MultipleWidget().widget(field, default, **attr)
        return wgt

    def define_tables(self):
        def platform_default(table, version):
            if db(db.platform).isempty():
                db.platform.insert(name='Onnix Sistemas')
            return

        db.define_table('platform',
            Field('name', 'string', label=T('Name')),
            migrate='platform.table',
            format='%(name)s')
        db.platform.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'platform.name')]
        self.set_table_defaults(db.platform, 1, on_update_data=platform_default)
        self.cruds += [dict(c='entries', f='platform')]


        db.define_table('customer',
            Field('name', 'string', label=T('Name')),
            Field('registry', 'string', label=T('Registry')),
            Field('phone', 'string', label=T('Phone')),
            Field('contact', 'string', label=T('Contact')),
            Field('email', 'string', label=T('Email')),
            Field('note', 'text', label=T('Note')),
            Field('is_active','boolean', label=T('Active')),
            migrate="customer.table",
            format='%(name)s')
        db.customer.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'customer.name')]
        db.customer.is_active.default = True
        self.set_table_defaults(db.customer, 0)
        self.cruds += [dict(c='entries', f='customer')]


        db.define_table('person',
            Field('name', 'string', label=T('Name')),
            Field('is_company', 'boolean', label=T('Company')),
            Field('person_type', 'list:string', label=T('Type')),
            Field('registry', 'string', label=T('Registry')),
            Field('phone', 'string', label=T('Phone')),
            Field('contact', 'string', label=T('Contact')),
            Field('email', 'string', label=T('Email')),
            Field('note', 'text', label=T('Note')),
            Field('is_active','boolean', label=T('Active')),
            plural=T('Persons and Companies'),
            singular=T('Person/Company'),
            migrate="person.table",
            format='%(name)s')
        db.person.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'person.name')]
        db.person.is_company.default = True
        db.person.person_type.requires = IS_IN_SET(EntriesModel.person_type, multiple=True)
        db.person.person_type.default = EntriesModel.person_type.keys()
        db.person.person_type.widget = EntriesModel.person_type_selects
        db.person.is_active.default = True
        self.set_table_defaults(db.person, 1, on_update_data=EntriesModel.convert_customer)
        self.cruds += [dict(c='entries', f='person')]


        db.define_table('company',
            Field('name', 'string', label=T('Name')),
            Field('registry', 'string', label=T('Registry')),
            migrate='company.table',
            format='%(name)s')
        db.company.name.default = 'My Company'
        db.company.registry.default = '00.000.000/0000-00'
        self.set_table_defaults(db.company, 1, on_update_data=ModelBase.insert_default)


        return

    @staticmethod
    def convert_customer(table, version):
        if db(table).isempty() and 'customer' in db:
            defs = table_default_values(table)
            for customer in db(db.customer).select():
                for col in db.customer.fields:
                    defs[col] = customer[col]
                table.insert(**defs)
        return

    @staticmethod
    def person_IS_IN_DB(only_active=True, types=None):
        query = (db.person.id > 0)
        if types:
            query &= db.person.person_type.contains(types, all=False)
        if only_active:
            query &= (db.person.is_active == True)

        return IS_IN_DB(db(query), db.person, db.person._format, orderby=db.person.name)
