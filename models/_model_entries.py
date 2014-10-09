# -*- coding: utf-8 -*-

from onx_model import ModelBase

class EntriesModel(ModelBase):

    def define_tables(self):

        db.define_table('platform',
            Field('name', 'string', label=T('Name')),
            migrate="platform.table",
            format='%(name)s')
        db.platform.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'platform.name')]    

        db.define_table('customer',
            oplink_field,
            Field('name', 'string', label=T('Name')),
            Field('phone', 'string', label=T('Phone')),
            Field('contact', 'string', label=T('Contact')),
            Field('email', 'string', label=T('Email')),
            Field('note', 'text', label=T('Note')),
            Field('is_active','boolean', label=T('Active')),
            migrate="customer.table",
            format='%(name)s')
        db.customer.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'customer.name')]
        db.customer.is_active.default = True
        return  

    def create_defaults(self):
        if db(db.platform).isempty():
            db.platform.insert(name='Onnix Sistemas')
