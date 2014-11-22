# -*- coding: utf-8 -*-
from gluon.html import XML, INPUT, A, SPAN, URL, DIV, UL, BUTTON, LI, FIELDSET, CAT, SELECT, TEXTAREA, LABEL
from gluon.globals import current
from gluon.sqlhtml import SQLFORM
from gluon.dal import Table
from gluon.storage import Storage
from gluon.http import redirect, HTTP


class PageConfig(object):
    '''
    Configuração da pagina

    A inclusão dos arquivos na pagina funcionariam perfeitamente se não fosse a questão do LOAD.
    Se em um LOAD tiver widget, o arquivo .js não será adicionado. Por isso deverá ser usado o 
    metodo CustomWidget().widget_files(), na função do controller
    '''
    def __init__(self, **kwargs):
        self.header_files = dict()
        self.footer_files = dict()

    def reset_files(self):
        self.header_files = dict()
        self.footer_files = dict()      
        return

    def include_files(self, files):
        css_template = '<link href="%s" rel="stylesheet" type="text/css"/>' 
        js_template = '<script src="%s" type="text/javascript"></script>'

        hfiles = []
        for k in files:
            f = files[k]
            if f.endswith('.js'):
                hfiles.append(js_template % f)
            elif f.endswith('.css'):
                hfiles.append(css_template % f)

        return XML('\n'.join([f for f in hfiles]))  


    def include_header_files(self):
        return self.include_files(self.header_files)


    def include_footer_files(self):
        return self.include_files(self.footer_files)


def remove_menu_origin():
    url_vars = current.request.vars.copy()
    if 'origin' in url_vars:
        del url_vars['origin']
    return url_vars


def formstyle_onx(form, fields):
    form.add_class('form-horizontal')
    parent = FIELDSET()
    for id, label, controls, help in fields:
        # wrappers
        _help = SPAN(help, _class='help-block')
        # embed _help into _controls
        _controls = DIV(controls, _help, _class='controls')
        # submit unflag by default
        _submit = False

        if isinstance(controls, INPUT):
            controls.add_class('span4')
            if controls['_type'] == 'submit':
                # flag submit button
                _submit = True
                controls['_class'] = 'btn btn-primary'
            if controls['_type'] == 'file':
                controls['_class'] = 'input-file'
            if controls['_type'] == 'checkbox':
                controls['_class'] = 'input-checkbox'

        # For password fields, which are wrapped in a CAT object.
        if isinstance(controls, CAT) and isinstance(controls[0], INPUT):
            controls[0].add_class('span4')

        if isinstance(controls, SELECT):
            controls.add_class('span4')

        if isinstance(controls, TEXTAREA):
            controls.add_class('span4')

        if isinstance(label, LABEL):
            label['_class'] = 'control-label'

        if _submit:
            # submit button has unwrapped label and controls, different class
            parent.append(DIV(label, controls, _class='row-fluid form-actions', _id=id))
            # unflag submit (possible side effect)
            _submit = False
        else:
            # unwrapped label
            parent.append(DIV(label, _controls, _class='row-fluid', _id=id))
    return parent


class ONXFORM(object):

    """
    SQLFORM(
        table, 
        record=None,
        deletable=False, 
        linkto=None,
        upload=None, 
        fields=None, 
        labels=None,
        col3={}, 
        submit_button='Submit',
        delete_label='Check to delete:',
        showid=True, 
        readonly=False,
        comments=True, 
        keepopts=[],
        ignore_rw=False, 
        record_id=None,
        formstyle='table3cols',
        buttons=['submit'], 
        separator=': ',
        **attributes)
    """

    ACTIONS = ['new', 'read', 'update', 'delete', 'select']

    customize_default = dict(
        on_manager_extra_links=lambda self, row: [],
        on_grid_orderby=lambda self:None,
        on_before_init=lambda self, action: None,
        on_after_init=lambda self, form, action: None,
        on_navegate=lambda self, nav, action: None,
        on_fields_list=lambda self, action: None,
        on_form_success=lambda form:None,
        )

    def __init__(self, table):
        self.table = table
        self.view_layout = None
        self.customize = Storage(self.customize_default)
        self.is_modal = False
        self.modal_cancel_onclick = None
        self.nav = None
        return


    @staticmethod
    def navegate():
        request = current.request
        session = current.session

        url_vars = remove_menu_origin()

        vredirect = url_vars.get('redirect')
        vnext = url_vars.get('next') or url_vars.get('_next')
        vprevious= url_vars.get('previous') or url_vars.get('_previous')
        if 'breadcrumbs' in session:
            last_url = session.breadcrumbs.last_url()
        else:
            last_url = None
        current_url = URL(c=request.controller, f=request.function, vars=url_vars)
        
        next = vnext or vredirect or last_url or current_url
        previous = vprevious or vredirect or last_url or current_url

        navegate = Storage(
            next=next,
            previous=previous,
            )
        return navegate

    def _form_buttons(self):
        T = current.T
        if self.is_modal and self.modal_cancel_onclick:
            btn_cancel = A(T('Cancel'), _class='btn', 
                _href='javascript:void(0);', 
                _onclick=self.modal_cancel_onclick)
        else:
            btn_cancel = A(T('Cancel'), _class='btn', _href=self.nav.previous)

        buttons = [
            INPUT(_type='submit', _value=T('Submit'), _class='btn btn-success'),
            btn_cancel,
            ]
        return buttons

    def do_form_new(self):
        response = current.response
        T = current.T
        action = 'new'

        response.title = T(self.table._plural)
        response.subtitle = T('New Record')
        response.breadcrumbs = response.subtitle

        buttons = self._form_buttons()

        self.customize.on_before_init(self, action)
        form = SQLFORM(
            self.table,
            buttons=buttons,
            formstyle=formstyle_onx,
            fields=self.customize.on_fields_list(self, action),
            )
        self.customize.on_after_init(self, form, action)

        attr = dict()
        if not self.is_modal:
            attr['next'] = self.nav.next
        attr['onsuccess'] = self.customize.on_form_success

        if form.process(**attr).accepted:
            response.flash = T('Record Created')
        elif form.errors:
            response.flash = form.errors
        return dict(content=form)


    def do_form_read(self):
        response = current.response
        request = current.request
        T = current.T
        table = self.table
        action = 'read'

        record = None
        if request.args(1) and request.args(1).isdigit():
            record = table[ int(request.args[1]) ]
        
        if not record: raise HTTP(404, 'Record ID invalid!')

        if isinstance(table._format,str):
            record_label = table._format % record
        else:
            record_label = table._format(record)

        response.title = T(table._plural)
        response.subtitle = T('View')+': '+record_label
        response.breadcrumbs = record_label


        buttons = [
            A(T('Back'), _class='btn', _href=self.nav.previous),
            ]    

        self.customize.on_before_init(self, action)
        form = SQLFORM(
            table, 
            record=record,
            readonly=True,
            formstyle=formstyle_onx,
            fields=self.customize.on_fields_list(self, action),
            )
        form[0].append(DIV(buttons))
        self.customize.on_after_init(self, form, action)
        return dict(content=form)


    def do_form_update(self):
        response = current.response
        request = current.request
        T = current.T
        table = self.table
        action = 'update'

        record = None
        if request.args(1) and request.args(1).isdigit():
            record = table[ int(request.args[1]) ]
        
        if not record: raise HTTP(404, 'Record ID invalid!')

        if isinstance(table._format,str):
            record_label = table._format % record
        else:
            record_label = table._format(record)

        response.title = T(table._plural)
        response.subtitle = T('Editing')+': '+record_label
        response.breadcrumbs = record_label

        buttons = self._form_buttons()

        self.customize.on_before_init(self, action)
        form = SQLFORM(
            table,
            record=record,
            buttons=buttons, 
            deletable=False,
            formstyle=formstyle_onx,
            fields=self.customize.on_fields_list(self, action),
            )
        self.customize.on_after_init(self, form, action)

        attr = dict()
        if not self.is_modal:
            attr['next'] = self.nav.next
        attr['onsuccess'] = self.customize.on_form_success

        if form.process(**attr).accepted:
            response.flash = T('Record Updated')
        elif form.errors:
            response.flash = form.errors
        return dict(content=form)


    def do_form_delete(self):
        response = current.response
        request = current.request
        T = current.T
        db = current.db
        table = self.table
        action = 'delete'

        record = None
        if request.args(1) and request.args(1).isdigit():
            record = table[ int(request.args[1]) ]
        
        if not record: raise HTTP(404, 'Record ID invalid!')

        if request.args(2) == 'confirmed':
            try:
                db(table.id == record.id).delete()
                response.flash = T('Record Deleted')
                redirect(self.nav.next)
            except Exception, e:
                raise e
        else:
            if isinstance(table._format,str):
                record_label = table._format % record
            else:
                record_label = table._format(record)

            response.title = T(table._plural)
            response.subtitle = T('Confirm delete "%s"?') % record_label
            response.breadcrumbs = T('Delete Record')

            request.args.append('confirmed')
            buttons = [
                A(T('Delete'), _class='btn btn-danger', _href=URL(c=request.controller, f=request.function, args=request.args, vars=remove_menu_origin())),
                SPAN(' '),
                A(T('Cancel'), _class='btn', _href=self.nav.previous),
                ]    

            self.customize.on_before_init(self, action)
            form = SQLFORM(
                table, 
                record=record,
                readonly=True,
                formstyle=formstyle_onx,
                fields=self.customize.on_fields_list(self, action),
                )
            form[0].insert(0, DIV(buttons))
            self.customize.on_after_init(self, form, action)
            return dict(content=form)


    def manager_menu(self, row):
        request = current.request
        T = current.T

        menu = []
        menu += [A(
                SPAN(_class='icon icon-pencil'),
                SPAN(T('Edit')),
                _href=URL(c=request.controller, f=request.function, args=['update', row.id], vars=remove_menu_origin()))]
        menu += [A(
                SPAN(_class='icon icon-trash'),
                SPAN(T('Remove')),
                _href=URL(c=request.controller, f=request.function, args=['delete', row.id], vars=remove_menu_origin()))]

        extra = self.customize.on_manager_extra_links(self, row)
        if len(extra):
            menu += [LI(_class='divider')]
            menu += extra
        return menu


    def grid_menu(self, row):
        T = current.T

        caption = T('Manager')
        menu = DIV(

            BUTTON(
            SPAN(_class='fa fa-bars'), SPAN(' '),
            SPAN(caption),
            _href='javascript:void(0);', 
            _class='btn btn-small dropdown-toggle',
            **{'_data-toggle':'dropdown', '_aria-expanded':'false'}),
            UL(self.manager_menu(row), _class='dropdown-menu stay-open pull-right', _role='menu'),
            _class='btn-group'
            )
        return menu


    def grid_links(self):
        links = [lambda row: self.grid_menu(row)]
        return links


    def do_grid_select(self):
        response = current.response
        T = current.T
        action = 'select'

        response.title = T(self.table._plural)
        response.subtitle = T('Listing')
        response.breadcrumbs = response.title

        exportclasses = dict(
            csv_with_hidden_cols=False,
            json=False,
            tsv_with_hidden_cols=False,
            tsv=False
        )    

        links = self.grid_links()

        ui = dict(
            widget='',
            header='',
            content='',
            default='',
            cornerall='',
            cornertop='',
            cornerbottom='pagination',
            button='btn',
            buttontext='buttontext button',
            buttonadd='icon plus',
            buttonback='icon leftarrow',
            buttonexport='icon downarrow',
            buttondelete='icon trash',
            buttonedit='icon pen',
            buttontable='icon rightarrow',
            buttonview='icon magnifier'
            )

        self.customize.on_before_init(self, action)
        grid = SQLFORM.grid(
            self.table,
            fields=self.customize.on_fields_list(self, action),
            #field_id=None,
            #left=None,
            #headers={},
            orderby=self.customize.on_grid_orderby(self),
            #groupby=None,
            #searchable=True,
            #sortable=True,
            #paginate=20,
            deletable=False,
            editable=False,
            details=False,
            #selectable=None,
            #create=True,
            #csv=True,
            links=links,
            #links_in_grid=True,
            #upload='<default>',
            #args=[],
            #user_signature=True,
            #maxtextlengths={},
            maxtextlength=30,
            #onvalidation=None,
            #oncreate=None,
            #onupdate=None,
            #ondelete=None,
            #sorter_icons=(XML('&#x2191;'), XML('&#x2193;')),
            ui=ui,
            #showbuttontext=True,
            _class="table table-condensed table-condensed table-hover",
            #formname='web2py_grid',
            #search_widget='default',
            #ignore_rw = False,
            #formstyle = 'table3cols',
            exportclasses=exportclasses,
            #formargs={},
            #createargs={},
            #editargs={},
            #viewargs={},
            #buttons_placement = 'right',
            #links_placement = 'right',
            )    
        self.customize.on_after_init(self, grid, action)
        return dict(content=grid)


    def validate_action(self):
        request = current.request

        action = request.args(0) or 'select'
        if action not in ONXFORM.ACTIONS:
            raise HTTP(404, 'Action "%s" not found!' % action)
        return action


    def get_current_action(self):
        action = self.validate_action()

        self.nav = ONXFORM.navegate()
        self.customize.on_navegate(self, self.nav, action)        

        if action == 'new':
            content = self.do_form_new()
        elif action == 'read':
            content = self.do_form_read()
        elif action == 'update':
            content = self.do_form_update()
        elif action == 'delete':
            content = self.do_form_delete()
        elif action == 'select':
            content = self.do_grid_select()
        else:
            content = None

        generic_view = 'others/generic_modal.load' if self.is_modal else 'others/generic_crud.html'
        response = current.response
        response.view = self.view_layout or generic_view

        return content


    @staticmethod
    def make(table):
        """
        http://..../[app]/[controller]/[function]/[*]  --> select
        http://..../[app]/[controller]/[function]/new/
        http://..../[app]/[controller]/[function]/read/[id]
        http://..../[app]/[controller]/[function]/update/[id]
        http://..../[app]/[controller]/[function]/delete/[id]
        http://..../[app]/[controller]/[function]/select/[**keywords]
        """
        oform = ONXFORM(table)
        content = oform.get_current_action()
        return content


class Breadcrumbs(object):

    def __init__(self):
        self.items = []
        return

    def reset(self, home_title, home_url):
        self.items = [(home_title, home_url)]

    def delete_item(self, index):
        while len(self.items) > index: 
            del self.items[-1]

    def add(self, title, url, reset=False):
        if reset:
            self.delete_item(1)
        else:
            for i, (t, u) in enumerate(self.items):
                from urlparse import urlparse
                if urlparse(u).path == urlparse(url).path:
                    self.delete_item(i)
                    break
        self.items.append( (title, url) )

    def last_url(self):
        if len(self.items):
            t, u = self.items[-1]
        else:
            u = None
        return u