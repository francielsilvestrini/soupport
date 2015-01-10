# -*- coding: utf-8 -*-
from gluon.storage import Storage
from gluon.html import URL

class ModelBase(object):
    '''
    Classe base para definição dos models

    Diferente dos plugins, essa metodologia deixa uma nomenclatura mais favoravel,
    e pode ser reutilizar sem problemas.
    '''

    def __init__(self):
        self.cruds = []
        self.crud_controller = 'default'
        self.crud_start = 0

        #self.table_defaults = [(table, version, on_update_data(table, version))]
        self.table_defaults = []
        return

    def __repr__(self):
        return "Model: %s" % self.name

    def define_tables(self):
        '''
        Sobrepor com as definições do model especifico
        '''
        return

    def validate_required(self, db, tables):
        '''
        Valida se a tabela está definida no banco de dados
        '''
        for tname in tables:
            if not tname in db.tables:
                raise Exception('Table "%s" no defined!' % tname)

    def model_define(self):
        self.define_tables()
        self.create_defaults()
        return

    def get_crud_menus(self, project):
        for crud in self.cruds:
            project.append_menu(
                name=crud,
                caption=db[crud]._plural,
                controller=self.crud_controller,
                function=crud[self.crud_start:],
            )
        return


    def set_table_defaults(self, table, version, on_update_data=None):
        self.table_defaults.append( (table, version, on_update_data) )
        return


    def create_defaults(self):
        def save_version(table_name, version):
            db.table_version.update_or_insert(
                db.table_version.table_name == table_name, **dict(table_name=table_name, version=version))
            return

        for table, version, on_update_data in self.table_defaults:
            if version == 0:
                continue

            old_version = db(db.table_version.table_name == table._tablename).select().first()
            if old_version and old_version.version >= version:
                continue

            try:
                if db(table).isempty():
                    if on_update_data:
                        on_update_data(table, version)
                else:
                    defs = table_default_values(table)
                    for k in defs:
                        if db(table[k] == None).count() > 0:
                            db(table[k] == None).update(**{k:defs[k]})

                    if on_update_data:
                        on_update_data(table, version)
                save_version(table._tablename, version)
            except Exception, e:
                logger.error(str(e))
        return


    @staticmethod
    def insert_default(table, version):
        if db(table).isempty():
            defs = table_default_values(table)
            table.insert(**defs)
        return
