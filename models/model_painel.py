# -*- coding: utf-8 -*-
from datetime import date


class PainelModel(ModelBase):
    name = 'painel'

    @staticmethod
    def config():
        return db(db.painel.id > 0).select().first()


    @staticmethod
    def company():
        return db(db.company.id > 0).select().first()

    @staticmethod
    def read_config(key, default):
        try:
            config = PainelModel.config()
            return config[key] or default
        except Exception, e:
            return default

    @staticmethod
    def validate_factor(end_date):
        config = PainelModel.config()
        days = (end_date - config.winning_factor).days
        return '{:0>4d}'.format(days)


    system_languages = {
        'en': 'English',
        'pt-br': 'Português',
    }

    def define_tables(self):
        db.define_table('table_version',
            Field('table_name', 'string', label=T('Table Name')),
            Field('version', 'integer', label=T('Version')),
            migrate='table_version.table',
            format='%(table_name)s v(%(version)s)')
        self.set_table_defaults(db.table_version, 0)

        db.define_table('painel',
            Field('name', 'string', label=T('Name')),
            Field('last_update', 'integer', label=T('DB Update Sequence')),
            #MUL - initial date for validate contract/licence
            Field('winning_factor', 'date', label=T('Winning Factor')),
            #how many zeros will have the ticket. ex: 6, 000123
            Field('ticket_size', 'integer', label=T('Ticket Size')),
            #language
            Field('language', 'string', label=T('Language')),
            #UI google
            Field('google_analytics_id', 'string', label=T('Google Analytics')),
            migrate='painel.table',
            format='%(name)s')
        db.painel.name.default = 'Painel'
        db.painel.last_update.default = 0
        db.painel.winning_factor.default = date(2008, 05, 05)
        db.painel.ticket_size.default = 6
        db.painel.language.requires = IS_IN_SET(PainelModel.system_languages)
        db.painel.language.default = 'en'
        db.painel.google_analytics_id.default = None
        self.set_table_defaults(db.painel, 1, on_update_data=ModelBase.insert_default)

        db.define_table('log',
            Field('name', 'string', label=T('Name')),
            Field('level', 'string', label=T('Level')),
            Field('module', 'string', label=T('Module')),
            Field('func_name', 'string', label=T('Function Name')),
            Field('line_no', 'string', label=T('Line No')),
            Field('thread', 'string', label=T('Thread')),
            Field('thread_name', 'string', label=T('Thread Name')),
            Field('process', 'string', label=T('Process')),
            Field('message', 'text', label=T('Message')),
            Field('args', 'text', label=T('Args')),
            Field('log_date', 'date', label=T('Date')),
            migrate='log.table',
            format='%(id)s')
        db.log.log_date.default = request.now.today()

        return
