# -*- coding: utf-8 -*-

class ProjectPainel(ProjectBase):
    name = 'painel'

    def __init__(self):
        ProjectBase.__init__(self)
        self.caption=T('Painel')
        self.home=URL(c='painel', f='index')
        self.admin_required=True
        return


    def load_menus(self):
        self.append_menu(
            name='auth_user',
            caption='User',
            controller='user',
            function='auth_user',
            )
        self.append_menu(
            name='auth_group',
            caption='User Group',
            controller='user',
            function='auth_user',
            )
        return


    def sidebar(self):
        vars_menu = dict(origin='menu')
        toplinks = [
            (T('Home'), URL(c='painel', f='index', vars=vars_menu), 'icon-home'),
            (T('Config'), URL(c='painel', f='config', vars=vars_menu), 'fa fa-cogs'),
            (T('Company'), URL(c='painel', f='company', vars=vars_menu), 'fa fa-home'),
            (T('Database'), URL(c='painel', f='database', vars=vars_menu), 'fa fa-database'),
            (T('Users'), URL(c='painel', f='users', vars=vars_menu), 'fa fa-users'),
            (T('Development'), URL(c='painel', f='development', vars=vars_menu), 'fa fa-wrench'),
            (T('Licence'), URL(c='activity', f='licence', vars=vars_menu), 'fa fa-key'),
            ]
        accordion_menu = []
        return Storage(toplinks=toplinks, accordion_menu=accordion_menu)

registred_projects['painel'] = ProjectPainel