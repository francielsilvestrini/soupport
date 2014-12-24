# -*- coding: utf-8 -*-

class ProjectMUL(ProjectBase):


    def __init__(self):
        ProjectBase.__init__(self)
        self.caption=T('Management of User Licenses')
        self.home=URL(c='mul', f='index')
        return


    def load_menus(self):
        self.append_menu(
            name='customer', 
            caption=T('Customer'), 
            controller='entries', 
            function='customer',        
            )
        self.append_menu(
            name='mul_product', 
            caption=T('Product'), 
            controller='mul', 
            function='product',
            ) 
        self.append_menu(
            name='mul_contract', 
            caption=T('Contract'), 
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
                self.menus.customer,

                ]),

            ]
        return Storage(toplinks=toplinks, accordion_menu=accordion_menu)


registred_projects['mul'] = ProjectMUL