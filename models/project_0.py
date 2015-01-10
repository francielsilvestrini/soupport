# -*- coding: utf-8 -*-

from gluon.storage import Storage

class ProjectBase(object):


    def __init__(self):
        self.menus = Storage()
        self.load_menus()

        self.caption=T('Project Base'),
        self.home=URL(c='default', f='index'),
        self.admin_required=False,
        return


    def append_menu(self, name, caption, controller, function, icon='icon-file', new=True):
        if new:
            new_record=(T('New %s'%caption),  URL(c=controller, f=function, args=['new'], vars=dict(origin='menu')))
        else:
            new_record=None

        item = Storage(
            caption=T(caption),
            icon=icon,
            url=URL(c=controller, f=function, vars=dict(origin='menu')),
            new_record=new_record,
        )
        self.menus[name] = item
        return item


    def load_menus(self):
        '''
        self.append_menu(
            name='fleet_inventory_item',
            caption=T('Inventory Item'),
            controller='fleet',
            function='inventory_item',
            )
        '''
        return


    def sidebar(self):
        toplinks = [
            #(caption, url, icon),
            ]

        accordion_menu = [
            #(T('Entries'), 'accordion_entries', 'icon-folder-open',  [
            #    menus.fleet_inventory_item,
            #    ]),
            ]
        return Storage(toplinks=toplinks, accordion_menu=accordion_menu)
