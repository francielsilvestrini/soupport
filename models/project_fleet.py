# -*- coding: utf-8 -*-

class ProjectFleet(ProjectBase):


    def __init__(self):
        ProjectBase.__init__(self)
        self.caption=T('Fleet')
        self.home=URL(c='fleet', f='index')
        return


    def load_menus(self):
        self.append_menu(
            name='fleet_vehicle_type', 
            caption=T('Vehicle Type'), 
            controller='fleet', 
            function='vehicle_type',
            )
        self.append_menu(
            name='fleet_vehicle', 
            caption=T('Vehicle'), 
            controller='fleet', 
            function='vehicle',
            )       

        self.append_menu(
            name='O1_inventory_item', 
            caption=T('Inventory Item'), 
            controller='inventory', 
            function='inventory_item',
            )
        self.append_menu(
            name='O1_unit_of_measure', 
            caption=T('Unit of Measure'), 
            controller='inventory', 
            function='unit_of_measure',
            )
        self.append_menu(
            name='O1_system', 
            caption=T('System'), 
            controller='inventory', 
            function='system',
            )
        self.append_menu(
            name='O1_subsystem', 
            caption=T('Subsystem'), 
            controller='inventory', 
            function='subsystem',
            )
        self.append_menu(
            name='O1_system_item', 
            caption=T('System Item'), 
            controller='inventory', 
            function='system_item',
            )

        app_models['tire_control'].get_crud_menus(self)
      
        return


    def sidebar(self):
        if db(db.O2_vehicle.is_active == True).count() > 0:
            toplinks = LOAD(c='fleet', f='toplinks.load', vars=request.vars, ajax=True, content=loading)
        else:
            toplinks = [
                (T('Home'), self.home, 'icon-home'),
                ]

        accordion_menu = [
            (T('Entries'), 'accordion_entries', 'icon-folder-open',  [
                self.menus.fleet_vehicle,
                self.menus.fleet_vehicle_type,
                ]),
            (T('Inventory'), 'accordion_inventory', 'icon-folder-open',  [
                self.menus.O1_inventory_item,
                self.menus.O1_unit_of_measure,
                self.menus.O1_system,
                self.menus.O1_subsystem,
                self.menus.O1_system_item,
                ]),
            ]
        return Storage(toplinks=toplinks, accordion_menu=accordion_menu)


registred_projects['fleet'] = ProjectFleet