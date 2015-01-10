# -*- coding: utf-8 -*-

class EntriesModel(ModelBase):
    name = 'entries'

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


        db.define_table('company',
            Field('name', 'string', label=T('Name')),
            Field('registry', 'string', label=T('Registry')),
            migrate='company.table',
            format='%(name)s')
        db.company.name.default = 'My Company'
        db.company.registry.default = '00.000.000/0000-00'
        self.set_table_defaults(db.company, 1, on_update_data=ModelBase.insert_default)

        return