# -*- coding: utf-8 -*-

class ProjectActivity(ProjectBase):
    name = 'activity'

    def __init__(self):
        ProjectBase.__init__(self)
        self.caption=T('Activity')
        self.home=URL(c='activity', f='index')
        return


    def load_menus(self):
        app_models['entries'].get_crud_menus(self)
        return


    def sidebar(self):
        toplinks = [
            (T('Home'), URL(c='activity', f='index'), 'icon-home'),
            ]
        accordion_menu = []
        return Storage(toplinks=toplinks, accordion_menu=accordion_menu)


registred_projects['activity'] = ProjectActivity