# -*- coding: utf-8 -*-

from onx_model import ModelBase

class PainelModel(ModelBase):
    name = 'painel'

    def define_tables(self):
        db.define_table('painel',
            Field('name', 'string', label=T('Name')),
            Field('last_update', 'integer', label=T('DB Update Sequence')),
            Field('winning_factor', 'date', label=T('Winning Factor')),            
            migrate='painel.table',
            format='%(name)s')
        db.painel.name.default = 'Painel'
        db.painel.last_update.default = 0   
        return

    def create_defaults(self):
        if db(db.painel).isempty():
            defaults = table_default_values(db.painel)
            db.painel.insert(**defaults)
        return

    def apply_updates(self):
    	painel = db(db.painel.id > 0).select().first()

    	def upd_customer_is_active():
    		db(db.customer.is_active == None).update(is_active=True)
    		return

    	def upd_customer_capitalize():
    		for row in db(db.customer.id > 0).select():
    			row.update_record(
    				name=row.name.capitalize(),
    				contact=row.contact.capitalize())
    		return

        def upd_sets():
            db(db.solicitation.priority == 'Normal').update(priority='normal')
            db(db.solicitation.priority == 'Warning').update(priority='warning')
            db(db.solicitation.priority == 'Damage').update(priority='damage')

            db(db.task.priority == 'Normal').update(priority='normal')
            db(db.task.priority == 'Warning').update(priority='warning')
            db(db.task.priority == 'Damage').update(priority='damage')

            db(db.task.status == 'Analysis').update(status='analysis')
            db(db.task.status == 'Development').update(status='development')
            db(db.task.status == 'Test').update(status='test')
            db(db.task.status == 'Released').update(status='released')

            db(db.task.test_status == 'Waiting').update(test_status='waiting')
            db(db.task.test_status == 'Success').update(test_status='success')
            db(db.task.test_status == 'Error').update(test_status='error')
            db(db.task.test_status == 'Retest').update(test_status='retest')

            db(db.test.test_result == 'Success').update(test_result='success')
            db(db.test.test_result == 'Error').update(test_result='error')

            db(db.solicitation.priority == '1').update(priority='normal')
            db(db.solicitation.priority == '2').update(priority='warning')
            db(db.solicitation.priority == '3').update(priority='damage')

            db(db.task.priority == '1').update(priority='normal')
            db(db.task.priority == '2').update(priority='warning')
            db(db.task.priority == '3').update(priority='damage')

            db(db.task.status == '1').update(status='analysis')
            db(db.task.status == '2').update(status='development')
            db(db.task.status == '3').update(status='test')
            db(db.task.status == '4').update(status='released')

            db(db.task.test_status == '1').update(test_status='waiting')
            db(db.task.test_status == '2').update(test_status='success')
            db(db.task.test_status == '3').update(test_status='error')
            db(db.task.test_status == '4').update(test_status='retest')

            db(db.test.test_result == '1').update(test_result='success')
            db(db.test.test_result == '2').update(test_result='error')            
            return

    	def update_function(id, function):
    		if id > painel.last_update:
    			function()
    			painel.update_record(last_update=id)
    		return

    	update_function(001, upd_customer_is_active)
    	update_function(003, upd_customer_capitalize)
        update_function(004, upd_sets)
    	return

