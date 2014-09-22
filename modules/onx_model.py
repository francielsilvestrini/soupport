# -*- coding: utf-8 -*-

class ModelBase(object):
    ''' 
    Classe base para definição dos models
    
    Diferente dos plugins, essa metodologia deixa uma nomenclatura mais favoravel,
    e pode ser reutilizar sem problemas.
    '''
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

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
