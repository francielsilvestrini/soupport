# -*- coding: utf-8 -*-

from onx_model import ModelBase

class PainelModel(ModelBase):

    def define_tables(self):
        db.define_table('painel',
            Field('name', 'string', label=T('Name')),
            Field('last_update', 'integer', label=T('DB Update Sequence')),
            migrate='painel.table',
            format='%(name)s')
        db.painel.name.default = 'Painel'
        db.painel.last_update.default = 0   
        return

    def create_defaults(self):
        if db(db.painel).isempty():
            defaults = my_default_values(db.painel)
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
            db(db.solicitation.priority == 'Normal').update(priority='1')
            db(db.solicitation.priority == 'Warning').update(priority='2')
            db(db.solicitation.priority == 'Damage').update(priority='3')

            db(db.task.priority == 'Normal').update(priority='1')
            db(db.task.priority == 'Warning').update(priority='2')
            db(db.task.priority == 'Damage').update(priority='3')

            db(db.task.status == 'Analysis').update(status='1')
            db(db.task.status == 'Development').update(status='2')
            db(db.task.status == 'Test').update(status='3')
            db(db.task.status == 'Released').update(status='4')

            db(db.task.test_status == 'Waiting').update(test_status='1')
            db(db.task.test_status == 'Success').update(test_status='2')
            db(db.task.test_status == 'Error').update(test_status='3')
            db(db.task.test_status == 'Retest').update(test_status='4')

            db(db.test.test_result == 'Success').update(test_result='1')
            db(db.test.test_result == 'Error').update(test_result='2')
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

