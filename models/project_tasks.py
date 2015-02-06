# -*- coding: utf-8 -*-

class ProjectTasks(ProjectBase):
    name = 'tasks'

    def __init__(self):
        ProjectBase.__init__(self)
        self.caption=T('Tasks')
        self.home=URL(c='tasks', f='index')
        return


    def load_menus(self):
        app_models['commom'].get_crud_menus(self)
        app_models['entries'].get_crud_menus(self)
        app_models['tasks'].get_crud_menus(self)

        self.append_menu('tasks', 'index')
        self.append_menu('tasks', 'my_tasks')
        self.append_menu('tasks', 'waiting_tests')
        self.append_menu('tasks', 'solicitation_detail')
        self.append_menu('tasks', 'solicitation_to_task')
        self.append_menu('tasks', 'task_detail')
        self.append_menu('tasks', 'tests')
        self.append_menu('tasks', 'release_history')
        self.append_menu('tasks', 'test_history')
        return


    def sidebar(self):
        toplinks = [
            (T('Home'), URL(c='tasks', f='index'), 'icon-home'),
            (self.menus['tasks_solicitation'], True),
            (self.menus['tasks_task'], True),
            ]

        accordion_menu = [
            (T('Entries'), 'accordion_entries', 'icon-folder-open',  [
                self.menus['tasks_solicitation'],
                self.menus['tasks_task'],
                self.menus['tasks_releases'],
                self.menus.entries_person,
                self.menus['tags_tag'],

                ]),

            ]
        return Storage(toplinks=toplinks, accordion_menu=accordion_menu)


registred_projects['tasks'] = ProjectTasks