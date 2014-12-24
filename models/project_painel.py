# -*- coding: utf-8 -*-

class ProjectPainel(ProjectBase):


    def __init__(self):
        ProjectBase.__init__(self)
        self.caption=T('Painel')
        self.home=URL(c='painel', f='index')
        self.admin_required=True
        return


    def load_menus(self):
        self.append_menu(
            name='auth_user', 
            caption=T('User'), 
            controller='user', 
            function='auth_user',
            )
        self.append_menu(
            name='auth_group', 
            caption=T('User Group'), 
            controller='user', 
            function='auth_user',
            )       
        return


    def sidebar(self):
        return None

registred_projects['painel'] = ProjectPainel