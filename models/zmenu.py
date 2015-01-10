# -*- coding: utf-8 -*-

response.meta.author = 'Onnix Desenv <desenv@onnixsistemas.com.br>'
response.meta.description = 'Onnix Sistemas <www.onnixsistemas.com.br>'
response.meta.keywords = 'onnix sistemas python web2py'
response.meta.generator = 'Web2py Web Framework & Python & SQLite & HTMl5 & CSS3 & JS & jQuery'
response.google_analytics_id = PainelModel.read_config('google_analytics_id', None)# 'UA-45957540-1'

response.language = PainelModel.read_config('language', 'en')
T.force(response.language)

response.app_version = ('1.0', '2015-01-03')
response.logo = A(SPAN('erp4my',
    SPAN(' '),
    SMALL('ONNIX SISTEMAS'),
    SPAN(' '),
    SMALL(response.app_version[0], _title=response.app_version[1]),
    _class="brand",_href='http://www.onnixsistemas.com.br'))
#response.title = request.application.replace('_',' ').title()
response.title = 'Onnix Sistemas'
response.subtitle = ''


#response.page_alerts = [(title, alert, alert_class)]
response.page_alerts = []


from onx_views import Breadcrumbs
if not 'breadcrumbs' in session:
    session.breadcrumbs = Breadcrumbs()


response.project_default = 'painel'
response.projects = Storage()
response.menu = []

def _menu_projects():

    user_projects = ['activity', 'painel']
    user_projects += ['tasks', 'mul', 'fleet']
    user_projects += ['fleet']
    user_projects += session.get('active_projects', [])

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
