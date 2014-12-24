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

#response.page_alerts = [(title, alert, alert_class)]
response.page_alerts = []
loading = DIV([DIV(_id="fountainG_%s"%i, _class="fountainG") for i in range(8)], _id="fountainG")


from onx_views import Breadcrumbs
if not 'breadcrumbs' in session: 
    session.breadcrumbs = Breadcrumbs()


response.project_default = 'activity'
response.projects = Storage()
response.menu = [] 

def _menu_projects():

    user_projects = ['activity', 'painel']
    #buscar do contrato
    user_projects += ['tasks', 'mul', 'fleet']

    unique_menu = dict()

    for pname in user_projects:
        cls = registred_projects.get(pname)
        if cls:
            prj = cls()
            if not prj.admin_required or auth.has_membership(role=ADMIN_ROLE):
                response.projects[pname] = Storage(
                    caption=prj.caption, 
                    url=prj.home, 
                    sidebar=prj.sidebar()
                    )
                for k in prj.menus:
                    unique_menu[k] = prj.menus.get(k)

    for k in unique_menu:
        menu = unique_menu[k]
        response.menu.append( (menu.caption, False, menu.url) )
        if menu.new_record:
            response.menu.append( (menu.new_record[0], False, menu.new_record[1]) )
    return

_menu_projects()
