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
        return

    def __repr__(self):
        return "Model: %s" % self.name

    def define_tables(self):
        '''
        Sobrepor com as definições do model especifico
        '''
        return

    def create_defaults(self):
        '''
        Caso o model tenha registros padrões, valores defaults
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
                caption=T(db[crud]._plural), 
                controller=self.crud_controller, 
                function=crud[self.crud_start:],
            )

        return