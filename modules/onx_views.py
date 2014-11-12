# -*- coding: utf-8 -*-
from gluon.html import XML, INPUT, A, SPAN, URL, DIV
from gluon.globals import current
from gluon.sqlhtml import SQLFORM
from gluon.dal import Table
from gluon.storage import Storage
from gluon.http import redirect


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


    @staticmethod    
    def navegate():
        request = current.request

        navegate = Storage(
            next= request.vars.get('next') or request.vars.get('_next') or URL(c=request.controller, f=request.function, vars=request.vars),
            previous= request.vars.get('previous') or request.vars.get('_previous') or URL(c=request.controller, f=request.function, vars=request.vars),
            )
        return navegate


    @staticmethod
    def do_form_new(table, **attr):
        response = current.response
        T = current.T

        response.title = T(table._plural)
        response.subtitle = T('New Record')

        navegate = ONXFORM.navegate()
        buttons = [
            INPUT(_type='submit', _value=T('Submit'), _class='btn btn-success'),
            A(T('Cancel'), _class='btn', _href=navegate.previous),
            ]    

        form = SQLFORM(
            table,
            buttons=buttons, 
            **attr
            )

        if form.process().accepted:
            response.flash = T('Record Created')
            redirect(navegate.next)
        elif form.errors:
            response.flash = form.errors
        return dict(content=form)


    @staticmethod
    def do_form_read(table, **attr):
        response = current.response
        request = current.request
        T = current.T

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

        navegate = ONXFORM.navegate()
        buttons = [
            A(T('Back'), _class='btn', _href=navegate.previous),
            ]    

        form = SQLFORM(
            table, 
            record=record,
            readonly=True,
            **attr
            )
        form[0].append(DIV(buttons))
        return dict(content=form)


    @staticmethod
    def do_form_update(table, **attr):
        response = current.response
        request = current.request
        T = current.T

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

        navegate = ONXFORM.navegate()
        buttons = [
            INPUT(_type='submit', _value=T('Submit'), _class='btn btn-success'),
            A(T('Cancel'), _class='btn', _href=navegate.previous),
            ]    

        form = SQLFORM(
            table,
            record=record,
            buttons=buttons, 
            deletable=False,
            **attr
            )

        if form.process().accepted:
            response.flash = T('Record Updated')
            redirect(navegate.next)
        elif form.errors:
            response.flash = form.errors
        return dict(content=form)


    @staticmethod
    def do_form_delete(table, **attr):
        response = current.response
        request = current.request
        T = current.T

        record = None
        if request.args(1) and request.args(1).isdigit():
            record = table[ int(request.args[1]) ]
        
        if not record: raise HTTP(404, 'Record ID invalid!')

        navegate = ONXFORM.navegate()
        if request.args(2) == 'confirmed':
            try:
                db(table.id == record.id).delete()
                response.flash = T('Record Deleted')
                redirect(navegate.next)
            except Exception, e:
                raise e
        else:
            if isinstance(table._format,str):
                record_label = table._format % record
            else:
                record_label = table._format(record)

            response.title = T(table._plural)
            response.subtitle = T('Confirm delete "%s"?') % record_label

            request.args.append('confirmed')
            buttons = [
                A(T('Delete'), _class='btn btn-danger', _href=URL(c=request.controller, f=request.function, args=request.args, vars=request.vars)),
                SPAN(' '),
                A(T('Cancel'), _class='btn', _href=navegate.previous),
                ]    

            form = SQLFORM(
                table, 
                record=record,
                readonly=True,
                **attr
                )
            form[0].insert(0, DIV(buttons))
            return dict(content=form)


    @staticmethod
    def grid_link_edit(show_caption=True):
        response = current.response
        request = current.request
        T = current.T

        caption = T('Edit') if show_caption else ''
        link = lambda row: A(
                SPAN(_class='icon icon-pencil'),
                SPAN(caption),
                _href=URL(c=request.controller, f=request.function, args=['update', row.id], vars=request.vars), 
                _class='btn btn-small')
        return link


    @staticmethod
    def grid_link_delete(show_caption=True):
        response = current.response
        request = current.request
        T = current.T

        caption = T('Remove') if show_caption else ''
        link = lambda row: A(
                SPAN(_class='icon icon-trash'),
                SPAN(caption),
                _href=URL(c=request.controller, f=request.function, args=['delete', row.id], vars=request.vars), 
                _class='btn btn-small')
        return link

    @staticmethod
    def do_grid_select(table_or_query, **attr):
        response = current.response
        request = current.request
        T = current.T

        if isinstance(table_or_query, Table):
            response.title = T(table_or_query._plural)
        else:
            response.title = T(request.function)    
        response.subtitle = T('Listing')

        exportclasses = dict(
            csv_with_hidden_cols=False,
            json=False,
            tsv_with_hidden_cols=False,
            tsv=False
        )    

        links = []
        extra_links = attr.get('extra_links', [])
        links += [link for link in extra_links]

        if attr.get('deletable', True):
            links += [ONXFORM.grid_link_edit()]
        if attr.get('editable', True):
            links += [ONXFORM.grid_link_delete()]
          
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

        grid = SQLFORM.grid(
            table_or_query,
            #fields=None,
            #field_id=None,
            #left=None,
            #headers={},
            #orderby=None,
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
        return dict(content=grid)


    @staticmethod
    def validate_action():
        request = current.request

        action = request.args(0) or 'select'
        if action not in ONXFORM.ACTIONS:
            raise HTTP(404, 'Action "%s" not found!' % action)
        return action


    @staticmethod
    def actions_factory():
        actions = dict(
            new=ONXFORM.do_form_new,
            read=ONXFORM.do_form_read,
            update=ONXFORM.do_form_update,
            delete=ONXFORM.do_form_delete,
            select=ONXFORM.do_grid_select,
            )
        return actions        


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
        response = current.response

        action = ONXFORM.validate_action()    
        actions = ONXFORM.actions_factory()
        content = actions[action](table)

        response.view = 'others/generic_crud.html'
        return content
