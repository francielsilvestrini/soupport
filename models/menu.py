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

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
        (T('Home'), False, URL('default', 'index'), [])
]

#DEVELOPMENT_MENU = auth.is_logged_in() and auth.user.email == 'admin@admin.app'
DEVELOPMENT_MENU = True
#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def dev_menu():
        # shortcuts
        app = request.application
        ctr = request.controller
        # useful links to internal and external resources
        response.menu += [
            (SPAN('Admin', _class='highlighted'), False, None, [
                (T('My Sites'), False, URL('admin', 'default', 'site')),
                (T('This App'), False, URL('admin', 'default', 'design/%s' % app), [
                    (T('Controller'), False, URL('admin', 'default', 'edit/%s/controllers/%s.py' % (app, ctr))),
                    (T('View'), False, URL('admin', 'default', 'edit/%s/views/%s' % (app, response.view))),
                    (T('Layout'), False, URL('admin', 'default', 'edit/%s/views/layout.html' % app)),
                    (T('Stylesheet'), False, URL('admin', 'default', 'edit/%s/static/css/web2py.css' % app)),
                    (T('DB Model'), False, URL('admin', 'default', 'edit/%s/models/db.py' % app)),
                    (T('Menu Model'), False, URL('admin', 'default', 'edit/%s/models/menu.py' % app)),
                    (T('Database'), False, URL(app, 'appadmin', 'index')),
                    (T('Errors'), False, URL('admin', 'default', 'errors/' + app)),
                    (T('About'), False, URL('admin', 'default', 'about/' + app)),
                ]),

                (T('Access Control'), False, None, [
                    (T('Users'), False, URL('default', 'auth_user')),
                    (T('Groups'), False, URL('default', 'auth_group')),
                ]),

            ])]
if DEVELOPMENT_MENU: dev_menu()


if "auth" in locals(): auth.wikimenu() 

from gluon.storage import Storage
menus = Storage()
app_menus = dict()


def create_menus():

    def append_menu(name, caption, url, new_record, apps, icon='icon-file'):
        item = Storage(
            caption=caption,
            icon=icon,
            url=url,
            new_record=new_record,
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
        url=URL(c='entries', f='platform'),
        new_record=(T('New Platform'), URL(c='entries', f='platform', args=['new'])),
        apps=['soupport'],
        )
    append_menu(
        name='customer', 
        caption=T('Customer'), 
        url=URL(c='entries', f='customer'),
        new_record=(T('New Customer'), URL(c='entries', f='customer', args=['new'])),
        apps=['soupport'],
        )
    append_menu(
        name='tag', 
        caption=T('Tag'), 
        url=URL(c='tags', f='tag'),
        new_record=(T('New Tag'), URL(c='tags', f='tag', args=['new'])),
        apps=['soupport'],
        )
    append_menu(
        name='solicitation', 
        caption=T('Solicitation'), 
        url=URL(c='tasks', f='solicitation'),
        new_record=(T('New Solicitation'), URL(c='tasks', f='solicitation', args=['new'])),
        icon='icon-bullhorn',
        apps=['soupport'],
        )
    append_menu(
        name='task', 
        caption=T('Task'), 
        url=URL(c='tasks', f='task'),
        new_record=(T('New Task'), URL(c='tasks', f='task', args=['new'])),
        icon='icon-tasks',
        apps=['soupport'],
        )
    append_menu(
        name='releases', 
        caption=T('Releases'), 
        url=URL(c='tasks', f='releases'),
        new_record=(T('New Releases'), URL(c='tasks', f='releases', args=['new'])),
        icon='icon-tags',
        apps=['soupport'],
        )
    append_menu(
        name='auth_user', 
        caption=T('User'), 
        url=URL(c='user', f='auth_user'),
        new_record=(T('New User'), URL(c='user', f='auth_user', args=['new'])),
        apps=['soupport'],
        )
    append_menu(
        name='auth_group', 
        caption=T('User Group'), 
        url=URL(c='user', f='auth_user'),
        new_record=(T('New User Group'), URL(c='user', f='auth_group', args=['new'])),
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
        (T('New Solicitation'), menus.solicitation.new_record, 'icon-bullhorn'),
        (T('New Task'), menus.task.new_record, 'icon-tasks'),
        (T('Customers'), menus.customer.url, 'icon-file'),
        (T('Releases'), menus.releases.url, 'icon-tags'),
        ]

    accordion_menu = [
        (T('Entries'), 'accordion_entries', 'icon-folder-open',  [
            menus.solicitation,
            menus.task,
            menus.releases,
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
        sidebar=None),
    mul=Storage(
        caption=T('Management of User Licenses'),
        url=URL(c='mul', f='index'),
        admin_required=False, 
        sidebar=None),
    )
response.project_default = 'activity'