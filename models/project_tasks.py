# -*- coding: utf-8 -*-

class ProjectTasks(ProjectBase):


    def __init__(self):
        ProjectBase.__init__(self)
        self.caption=T('Tasks')
        self.home=URL(c='tasks', f='index')
        return


    def load_menus(self):
        self.append_menu(
            name='platform', 
            caption=T('Platform'), 
            controller='entries', 
            function='platform',
            )
        self.append_menu(
            name='customer', 
            caption=T('Customer'), 
            controller='entries', 
            function='customer',        
            )
        self.append_menu(
            name='tag', 
            caption=T('Tag'), 
            controller='tags', 
            function='tag',
            )
        self.append_menu(
            name='solicitation', 
            caption=T('Solicitation'), 
            controller='tasks', 
            function='solicitation',
            icon='icon-bullhorn',
            )
        self.append_menu(
            name='task', 
            caption=T('Task'), 
            controller='tasks', 
            function='task',
            icon='icon-tasks',
            )
        self.append_menu(
            name='releases', 
            caption=T('Releases'), 
            controller='tasks', 
            function='releases',
            icon='icon-tags',
            )
        return


    def sidebar(self):
        toplinks = [
            (T('Home'), URL(c='tasks', f='index'), 'icon-home'),
            (self.menus.solicitation.new_record[0], self.menus.solicitation.new_record[1], self.menus.solicitation.icon),
            (self.menus.task.new_record[0], self.menus.task.new_record[1], self.menus.task.icon),
            ]

        accordion_menu = [
            (T('Entries'), 'accordion_entries', 'icon-folder-open',  [
                self.menus.solicitation,
                self.menus.task,
                self.menus.releases,
                self.menus.customer,
                self.menus.tag,

                ]),

            ]
        return Storage(toplinks=toplinks, accordion_menu=accordion_menu)


registred_projects['tasks'] = ProjectTasks