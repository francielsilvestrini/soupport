# -*- coding: utf-8 -*-

response.meta.author = 'Onnix Desenv <desenv@onnixsistemas.com.br>'
response.meta.description = 'Onnix Sistemas <www.onnixsistemas.com.br>'
response.meta.keywords = 'onnix sistemas python web2py'
response.meta.generator = 'Web2py Web Framework & Python & SQLite & HTMl5 & CSS3 & JS & jQuery'
response.google_analytics_id = PainelModel.read_config('google_analytics_id', None)# 'UA-45957540-1'

response.language = PainelModel.read_config('language', 'pt-br')
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


response.project_default = 'activity'
response.projects = Dict()
response.menu = []
response.unique_menu = dict()
response.contract = None
if auth.is_logged_in() and auth.user.username != Settings.SUPER_USER:
    response.contract = MULModel.load_contract()

def _menu_projects():
    user_projects = ['activity', 'painel']
    if response.contract:
        for k in response.contract['items']:
            user_projects.append(k)
    else:
        user_projects = registred_projects.keys()

    for pname in user_projects:
        cls = registred_projects.get(pname)
        if not cls:
            continue

        prj = cls()
        if (not prj.admin_required) or (auth.is_logged_in() and auth.has_membership(role=Settings.ADMIN_ROLE)):
            response.projects[pname] = Dict(
                caption=prj.caption,
                url=prj.home,
                sidebar=prj.sidebar()
                )
            for k in prj.menus:
                if not response.unique_menu.get(k):
                    response.unique_menu[k] = prj.menus[k]
                    response.unique_menu[k]['projects'] = []
                response.unique_menu[k]['projects'] = [prj.name]

    for k in response.unique_menu:
        menu = response.unique_menu[k]
        if not menu.is_crud:
            continue
        response.menu.append( (menu.caption, False, menu.url) )
        if menu.new_record:
            response.menu.append( (menu.new_record[0], False, menu.new_record[1]) )
    return

_menu_projects()
