# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.app_version = '1.0'
response.logo = A(SPAN('soupport',
    SMALL(response.app_version), 
    SPAN(' '),
    SMALL('Onnix Sistemas'),
    _class="brand",_href=URL(f='index')))
#response.title = request.application.replace('_',' ').title()
response.title = 'Onnix Sistemas'
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Onnix Desenv <desenv@onnixsistemas.com.br>'
response.meta.description = 'Control calls and customer requests. Management tasks of development and testing.'
response.meta.keywords = 'web2py, python, framework, tasks, tests, solicitations'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None


from onx_views import Breadcrumbs
if not 'breadcrumbs' in session: 
    session.breadcrumbs = Breadcrumbs()


from gluon.storage import Storage
menus = Storage()
app_menus = dict()


def create_menus():

    def append_menu(name, caption, controller, function, apps, icon='icon-file'):
        item = Storage(
            caption=caption,
            icon=icon,
            url=URL(c=controller, f=function, vars=dict(origin='menu'), anchor='MENU'),
            new_record=(T('New %s'%caption),  URL(c=controller, f=function, args=['new'], vars=dict(origin='menu'))),
        )
        menus[name] = item

        for app_name in apps:
            if app_menus.get(app_name):
                app_menus[app_name].append(name)
            else:
                app_menus[app_name] = [name]

        return item

    append_menu(
        name='platform', 
        caption=T('Platform'), 
        controller='entries', 
        function='platform',
        apps=['soupport'],
        )
    append_menu(
        name='customer', 
        caption=T('Customer'), 
        controller='entries', 
        function='customer',        
        apps=['soupport'],
        )
    append_menu(
        name='tag', 
        caption=T('Tag'), 
        controller='tags', 
        function='tag',
        apps=['soupport'],
        )
    append_menu(
        name='solicitation', 
        caption=T('Solicitation'), 
        controller='tasks', 
        function='solicitation',
        icon='icon-bullhorn',
        apps=['soupport'],
        )
    append_menu(
        name='task', 
        caption=T('Task'), 
        controller='tasks', 
        function='task',
        icon='icon-tasks',
        apps=['soupport'],
        )
    append_menu(
        name='releases', 
        caption=T('Releases'), 
        controller='tasks', 
        function='releases',
        icon='icon-tags',
        apps=['soupport'],
        )
    append_menu(
        name='auth_user', 
        caption=T('User'), 
        controller='user', 
        function='auth_user',
        apps=['soupport'],
        )
    append_menu(
        name='auth_group', 
        caption=T('User Group'), 
        controller='user', 
        function='auth_user',
        apps=['soupport'],
        )
    return


create_menus()

app_name = 'soupport'
response.menu = [] 
for imenu in app_menus[app_name]:
    menu = menus[imenu]
    response.menu.append( (menu.caption, False, menu.url) )
    response.menu.append( (menu.new_record[0], False, menu.new_record[1]) )


def sidebar_tasks():
    toplinks = [
        (T('Home'), URL(c='tasks', f='index'), 'icon-home'),
        (menus.solicitation.new_record[0], menus.solicitation.new_record[1], menus.solicitation.icon),
        (menus.task.new_record[0], menus.task.new_record[1], menus.task.icon),
        ]

    accordion_menu = [
        (T('Entries'), 'accordion_entries', 'icon-folder-open',  [
            menus.solicitation,
            menus.task,
            menus.releases,
            menus.customer,
            menus.tag,

            ]),

        ]

    return Storage(toplinks=toplinks, accordion_menu=accordion_menu)

def sidebar_entries():
    toplinks = [
        (T('Home'), URL(c='entries', f='index'), 'icon-home'),
        (menus.customer.new_record[0], menus.customer.new_record[1], menus.customer.icon),
        ]

    accordion_menu = [
        (T('Entries'), 'accordion_entries', 'icon-folder-open',  [
            menus.customer,
            menus.platform,
            menus.tag,

            ]),

        ]

    return Storage(toplinks=toplinks, accordion_menu=accordion_menu)


#projects = {'project_name':(caption, index_page, admin_required, navbar),}
response.projects = Storage(
    tasks=Storage(
        caption=T('Tasks'), 
        url=URL(c='tasks', f='index'), 
        admin_required=False, 
        sidebar=sidebar_tasks()),
    activity=Storage(
        caption=T('Activity'), 
        url=URL(c='activity', f='index'), 
        admin_required=False, 
        sidebar=None),
    painel=Storage(
        caption=T('Painel'), 
        url=URL(c='painel', f='index'), 
        admin_required=True, 
        sidebar=None),
    entries=Storage(
        caption=T('Entries'), 
        url=URL(c='entries', f='index'),
        admin_required=False, 
        sidebar=sidebar_entries()),
    mul=Storage(
        caption=T('Management of User Licenses'),
        url=URL(c='mul', f='index'),
        admin_required=False, 
        sidebar=None),
    )
response.project_default = 'activity'