# -*- coding: utf-8 -*-
from gluon.html import XML, A, SPAN, URL, DIV, UL, LI, CAT, I, SCRIPT
from gluon.html import INPUT, BUTTON, FIELDSET, SELECT, TEXTAREA, LABEL
from gluon.globals import current
from gluon.sqlhtml import SQLFORM
from gluon.dal import Table
from gluon.storage import Storage
from gluon.http import redirect, HTTP


def _formstyle_onx(form, fields, is_modal):
    form.add_class('form-horizontal onx-form')
    input_class = {True: 'span8', False: 'span4'}
    parent = FIELDSET()
    for id, label, controls, help in fields:
        # wrappers
        _help = SPAN(help, _class='help-block')
        # embed _help into _controls

        if isinstance(controls, DIV):
            wgt = controls.elements('.onx-widget')
            if wgt:
                controls.insert(1,_help)
                _controls = DIV(controls, _class='controls')
            else:
                _controls = DIV(controls, _help, _class='controls')
        else:
            _controls = DIV(controls, _help, _class='controls')
        # submit unflag by default
        _submit = False

        if isinstance(controls, INPUT):
            controls.add_class(input_class[is_modal])
            if controls['_type'] == 'submit':
                # flag submit button
                _submit = True
                controls['_class'] = 'btn btn-success'
            if controls['_type'] == 'file':
                controls['_class'] = 'input-file'
            if controls['_type'] == 'checkbox':
                controls['_class'] = 'input-checkbox'

        # For password fields, which are wrapped in a CAT object.
        if isinstance(controls, CAT) and isinstance(controls[0], INPUT):
            controls[0].add_class(input_class[is_modal])

        if isinstance(controls, SELECT):
            controls.add_class(input_class[is_modal])

        if isinstance(controls, TEXTAREA):
            controls['_class'] = 'text %s' % 'span8' if is_modal else 'span6'

        if isinstance(label, LABEL):
            label['_class'] = 'control-label'

        if _submit:
            # submit button has unwrapped label and controls, different class
            parent.append(DIV(label, DIV(controls, _class='controls'), _class='row-fluid', _id=id))
            # unflag submit (possible side effect)
            _submit = False
        else:
            # unwrapped label
            parent.append(DIV(label, _controls, _class='row-fluid', _id=id))
    return parent


def formstyle_onx(form, fields):
    return _formstyle_onx(form, fields, False)


def formstyle_onx_modal(form, fields):
    return _formstyle_onx(form, fields, True)


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
        on_form_buttons=lambda self, action, buttons: buttons,
        on_grid_query=lambda self: None,
        on_hidden_fields=lambda self, action, record_id, hidden: None,
        )

    def __init__(self, table):
        self.table = table
        self.view_layout = None
        self.customize = Storage(self.customize_default)
        self.is_modal = False
        self.modal_cancel_onclick = None
        self.save_and_add_enabled = True
        self.child_controls = False
        self.nav = None
        return


    @staticmethod
    def get_btn_save():
        T = current.T
        btn_save = INPUT(_type='submit', _value=T('Save'), _class='btn btn-success')
        return btn_save

    def navegate(self, action):
        '''
        workflow
        # new
            cance:
            save and add:
            save and next:
        # read
            back:
            edit:
            new:
        # update
            cancel:
            save and add:
            save and next:
        # delete
            cancel:
            delete:

        '''
        request = current.request

        vredirect = request.get_vars.get('redirect')
        vnext = request.get_vars.get('next')
        vprevious= request.get_vars.get('previous')

        new_vars = clear_vars_navegate(request.get_vars)
        grid_url = URL(args=['select'], vars=new_vars)
        new_record = URL(args=['new'],  vars=new_vars)

        next = vnext or vredirect or grid_url
        previous = vprevious or vredirect or grid_url

        navegate = Storage(
            next=next,
            previous=previous,
            new_record=new_record,
            )

        self.customize.on_navegate(self, navegate, action)
        return navegate

    def get_form_buttons(self, action, record_id):
        T = current.T
        request = current.request
        new_vars = clear_vars_navegate(request.get_vars)

        btn_save = None
        btn_save_and_add = None
        btn_edit = None
        btn_delete = None
        btn_cancel = None
        btn_new = None

        if action in ['new', 'update']:
            btn_save = ONXFORM.get_btn_save()
            if self.save_and_add_enabled and not self.is_modal:
                btn_save_and_add = A(I(_class='fa fa-plus'),
                    _title=T('Save and Add'),
                    _class='btn',
                    _href='javascript:void(0);',
                    _onclick='submit_and_add(this);',
                    **{'_data-toggle':'tooltip'})

        if action in ['read']:
            new_vars['previous'] = URL(args=request.args, vars=request.get_vars)
            new_vars['origin'] = 'read'
            btn_edit = A(T('Edit'),
                _class='btn btn-primary',
                _style='margin-right:8px;',
                _href=URL(args=['update', record_id], vars=new_vars))
            btn_new = A(I(_class='fa fa-plus'),
                    _title=T('New Record'),
                    _class='btn',
                    _href=URL(args=['new'], vars=new_vars),
                    **{'_data-toggle':'tooltip'})

        if action in ['delete']:
            btn_delete = A(T('Delete'),
                _class='btn btn-danger',
                _style='margin-right:8px;',
                _href=URL(args=request.args, vars=request.get_vars))

        if action in ['read', 'delete']:
            btn_cancel = A(T('Back'), _class='btn', _href=self.nav.previous)
        else:
            if self.is_modal:
                if self.modal_cancel_onclick:
                    btn_cancel = A(
                        T('Cancel'),
                        _class='btn',
                        _href='javascript:void(0);',
                        _style='margin-right:8px;',
                        _onclick=self.modal_cancel_onclick)
            else:
                btn_cancel = A(T('Cancel'),
                    _class='btn',
                    _style='margin-right:8px;',
                    _href=self.nav.previous)

        buttons = dict(
            btn1_save=btn_save,
            btn2_save_and_add=btn_save_and_add,
            btn3_edit=btn_edit,
            btn4_delete=btn_delete,
            btn5_cancel=btn_cancel,
            btn6_new=btn_new)

        self.customize.on_form_buttons(self, action, buttons)
        btns = []
        for k in sorted(buttons):
            if buttons[k]:
                btns.append(buttons[k])
        return btns

    def js_submit_and_add(self):
        js = '''
            function submit_and_add(e) {
                var url = "%(url)s";
                var form = $(e).parents("form:first");
                $("input[name='_next']",form).val(url);
                $(form).submit();
            }
            ''' % {'url':self.nav.new_record}
        jq_script=SCRIPT(js, _type="text/javascript")
        return jq_script

    def get_hidden_fields(self, action, record_id):
        request = current.request
        hidden = dict()
        if not self.is_modal:
            save_redirect = self.nav.next
            if self.child_controls:
                new_vars = clear_vars_navegate(request.get_vars)
                save_redirect = URL(args=['read', '[id]'], vars=new_vars, url_encode=False)
            hidden['_next'] = save_redirect

        self.customize.on_hidden_fields(self, action, record_id, hidden)
        return hidden

    def do_form_new(self):
        response = current.response
        request = current.request
        T = current.T
        action = 'new'
        self.nav = self.navegate(action)

        response.title = T(self.table._plural)
        response.subtitle = T('New Record')
        response.breadcrumbs = '+'+response.title

        buttons = self.get_form_buttons(action, 0)

        self.customize.on_before_init(self, action)

        attr = dict(
            onsuccess=self.customize.on_form_success)
        hidden = self.get_hidden_fields(action, 0)
        if request.post_vars.get('_next'):
            hidden['_next'] = request.post_vars['_next']
        if hidden.get('_next'):
            attr['next'] = hidden['_next']

        form = SQLFORM(
            self.table,
            buttons=buttons,
            formstyle=formstyle_onx,
            fields=self.customize.on_fields_list(self, action),
            hidden=hidden,
            )
        if self.save_and_add_enabled:
            form[0].append(self.js_submit_and_add())
        self.customize.on_after_init(self, form, action)

        if form.process(**attr).accepted:
            response.flash = T('Record Created')
        elif form.errors:
            response.flash = form.errors
        return dict(content=form)


    def do_form_read(self, record_id):
        response = current.response
        request = current.request
        T = current.T
        table = self.table
        action = 'read'
        self.nav = self.navegate(action)

        record = None
        if isinstance(record_id, str):
            record_id = int(record_id)

        record = table[ record_id ]
        if not record: raise HTTP(404, 'Record ID invalid!')

        if isinstance(table._format,str):
            record_label = table._format % record
        else:
            record_label = table._format(record)

        response.title = T(table._plural)
        response.subtitle = T('View')+': '+record_label
        response.breadcrumbs = record_label


        buttons = self.get_form_buttons(action, record_id)

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


    def do_form_update(self, record_id):
        response = current.response
        T = current.T
        table = self.table
        action = 'update'
        self.nav = self.navegate(action)

        record = None
        if isinstance(record_id, str):
            record_id = int(record_id)

        record = table[ record_id ]
        if not record: raise HTTP(404, 'Record ID invalid!')

        if isinstance(table._format,str):
            record_label = table._format % record
        else:
            record_label = table._format(record)

        response.title = T(table._plural)
        response.subtitle = T('Editing')+': '+record_label
        response.breadcrumbs = record_label

        buttons = self.get_form_buttons(action, record_id)

        attr = dict(
            onsuccess=self.customize.on_form_success)
        hidden = self.get_hidden_fields(action, record.id)
        if hidden.get('_next'):
            attr['next'] = hidden['_next']

        self.customize.on_before_init(self, action)
        form = SQLFORM(
            table,
            record=record,
            buttons=buttons,
            deletable=False,
            formstyle=formstyle_onx,
            fields=self.customize.on_fields_list(self, action),
            hidden=hidden
            )
        if self.save_and_add_enabled:
            form[0].append(self.js_submit_and_add())
        self.customize.on_after_init(self, form, action)

        if form.process(**attr).accepted:
            response.flash = T('Record Updated')
        elif form.errors:
            response.flash = form.errors
        return dict(content=form)


    def do_form_delete(self, record_id):
        response = current.response
        request = current.request
        T = current.T
        db = current.db
        table = self.table
        action = 'delete'
        self.nav = self.navegate(action)

        if isinstance(record_id, str):
            record_id = int(record_id)

        record = table[ record_id ]
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
            buttons = self.get_form_buttons(action, record_id)

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

        new_vars = request.get_vars.copy()
        new_vars['origin'] = 'select'

        menu = []
        if self.child_controls:
            menu += [A(
                    SPAN(_class='icon icon-edit'),
                    SPAN(T('Edit Items')),
                    _href=URL(args=['read', row.id], vars=new_vars))]
        menu += [A(
                SPAN(_class='icon icon-pencil'),
                SPAN(T('Edit')),
                _href=URL(args=['update', row.id], vars=new_vars))]
        menu += [A(
                SPAN(_class='icon icon-trash'),
                SPAN(T('Remove')),
                _href=URL(args=['delete', row.id], vars=new_vars))]

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
    def do_grid_select(self):
        response = current.response
        request = current.request
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

        def _table_or_query():
            query = self.customize.on_grid_query(self)
            if not query:
                query = self.table
            return query

        self.customize.on_before_init(self, action)
        grid = SQLFORM.grid(
            _table_or_query(),
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
            ui=ONXFORM.ui,
            #showbuttontext=True,
            _class="table table-condensed table-hover resp-table",
            #formname='web2py_grid',
            #search_widget='default',
            #ignore_rw = False,
            #formstyle = 'table3cols',
            exportclasses=exportclasses,
            #formargs={},
            #createargs={'origin':'select'},
            #editargs={},
            #viewargs={},
            #buttons_placement = 'right',
            #links_placement = 'right',
            )
        self.customize.on_after_init(self, grid, action)
        return dict(content=grid)


    def validate_action(self, action):
        action = action or 'select'

        if action not in ONXFORM.ACTIONS:
            raise HTTP(404, 'Action "%s" not found!' % action)
        return action


    def execute_action(self, action, record_id):
        action = self.validate_action(action)

        if action == 'new':
            content = self.do_form_new()
        elif action == 'read':
            content = self.do_form_read(record_id)
        elif action == 'update':
            content = self.do_form_update(record_id)
        elif action == 'delete':
            content = self.do_form_delete(record_id)
        elif action == 'select':
            content = self.do_grid_select()
        else:
            content = None

        generic_view = 'others/generic_modal.load' if self.is_modal else 'others/generic_crud.html'
        response = current.response
        response.view = self.view_layout or generic_view

        return content


    def get_current_action(self):
        request = current.request
        content = self.execute_action(request.args(0), request.args(1))
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


    @staticmethod
    def child_item(action, parent_id, item_id, table_item,
        target, list_url, on_get_content, onsuccess=None):
        response = current.response

        if action == 'list':
            content = on_get_content(action)
            return dict(content=content)

        elif action == 'edit':
            response.view = 'others/generic_modal.load'

            content = on_get_content(action, item_id)
            if isinstance(content, dict):
                form = content['form']
                extra_js = content.get('extra_js', '')
            else:
                form = content
                extra_js = ''

            attr = dict(onsuccess=onsuccess)

            if form.process(**attr).accepted:
                response.js = "$('#dialog_modal').modal('hide');" if item_id > 0 else ""
                response.js += "web2py_component('%s','%s-load');" % (list_url, target)
                response.js += extra_js
            return dict(content=form)

        elif action == 'remove':
            content = on_get_content(action, item_id)
            if content == None:
                db(table_item.id == item_id).delete()
                content = True
            if content == True:
                response.flash=T('Removed with success!')
                response.js = "web2py_component('%s','%s-load');" % (list_url, target)
            return

