# -*- coding: utf-8 -*-

class ProjectFleet(ProjectBase):
    name = 'fleet'

    def __init__(self):
        ProjectBase.__init__(self)
        self.caption=T('Fleet')
        self.home=URL(c='fleet', f='index')
        return


    def load_menus(self):
        app_models['vehicle'].get_crud_menus(self)
        app_models['inventory'].get_crud_menus(self)
        app_models['tire_control'].get_crud_menus(self)
        app_models['maintenance'].get_crud_menus(self)
        app_models['entries'].get_crud_menus(self)

        self.append_menu('fleet', 'index')
        self.append_menu('fleet', 'dashboard')
        self.append_menu('fleet', 'change_status')
        self.append_menu('fleet', 'refueling')
        self.append_menu('fleet', 'odometer')
        self.append_menu('fleet', 'reset_odometer')
        self.append_menu('fleet', 'distance_traveled')
        self.append_menu('tire_control', 'create')
        self.append_menu('tire_control', 'manage')
        self.append_menu('tire_control', 'change_chassi')
        self.append_menu('tire_control', 'remove_tire')
        self.append_menu('tire_control', 'groove_annotation_print')
        self.append_menu('tire_control', 'groove_annotation')
        self.append_menu('inventory', 'components')
        self.append_menu('maintenance', 'create')
        self.append_menu('maintenance', 'manage')
        self.append_menu('maintenance', 'order')
        return


    def sidebar(self):
        if db(db.vehicle.is_active == True).count() > 0:
            toplinks = LOAD(c='fleet', f='toplinks.load', vars=request.vars, ajax=True, content=loading)
        else:
            toplinks = [
                (T('Home'), self.home, 'icon-home'),
                ]

        accordion_menu = [
            (T('Entries'), 'accordion_entries', 'icon-folder-open',  [
                self.menus['fleet_vehicle'],
                ]),
            (T('Inventory'), 'accordion_inventory', 'icon-folder-open',  [
                self.menus['inventory_inventory_item'],
                self.menus['inventory_unit_of_measure'],
                self.menus['inventory_system'],
                self.menus['inventory_subsystem'],
                self.menus['inventory_system_item'],
                ]),
            ]
        return Storage(toplinks=toplinks, accordion_menu=accordion_menu)


registred_projects['fleet'] = ProjectFleet