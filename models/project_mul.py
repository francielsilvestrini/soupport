# -*- coding: utf-8 -*-

class ProjectMUL(ProjectBase):
    name = 'mul'

    def __init__(self):
        ProjectBase.__init__(self)
        self.caption=T('Management of User Licenses')
        self.home=URL(c='mul', f='index')
        return


    def load_menus(self):
        app_models['entries'].get_crud_menus(self)

        self.append_menu(
            name='mul_product',
            caption='Product',
            controller='mul',
            function='product',
            )
        self.append_menu(
            name='mul_contract',
            caption='Contract',
            controller='mul',
            function='contract',
            )
        return


    def sidebar(self):
        toplinks = [
            (T('Home'), URL(c='mul', f='index'), 'icon-home'),
            ]

        accordion_menu = [
            (T('MUL'), 'accordion_entries', 'icon-folder-open',  [
                self.menus.mul_product,
                self.menus.mul_contract,
                self.menus.entries_person,

                ]),

            ]
        return Storage(toplinks=toplinks, accordion_menu=accordion_menu)


registred_projects['mul'] = ProjectMUL