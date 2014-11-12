# -*- coding: utf-8 -*-

from onx_model import ModelBase
from h5_widgets import MaskWidget 

class MULModel(ModelBase):
    name = 'mul'
    
    def define_tables(self):
        self.validate_required(db, ['platform', 'customer'])

        db.define_table('module',
            Field('platform_id', db.platform, label=T('Platform')),
            Field('code', 'string', label=T('Code')),
            Field('name', 'string', label=T('Name')),
            migrate='module.table',
            format='%(code)s - %(name)s')
        db.module.code.requires = [IS_NOT_EMPTY()]
        db.module.code.widget = MaskWidget(mask='0000').widget
        db.module.name.requires = [IS_NOT_EMPTY()]
        db.module.platform_id.requires = IS_IN_DB(db, db.platform, db.platform._format)

        '''

/MUL --> management of user licenses
    /platform    --> exemplo onnix erp (onnix erp e onnix fiscal)
        #modules --> 02,04,08,16,32...
    /contract    --> contrato entre o cliente e a plataforma
        #modules --> modulos liberados no contrato
    /history     --> historico do contrato eas liberações
    
        '''
        return  
