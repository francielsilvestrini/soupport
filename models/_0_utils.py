# -*- coding: utf-8 -*-

from gluon.custom_import import track_changes
track_changes(True)

loading = DIV([DIV(_id="fountainG_%s"%i, _class="fountainG") for i in range(8)], _id="fountainG")

## GLOBAL IMPORTS ##
from gluon.tools import prettydate
import uuid
from os import path
from gluon.sqlhtml import represent
from gluon.storage import Storage as Dict
import csv
import os
## END GLOBAL IMPORTS ##

SMALL = lambda x, **kwargs: XML(TAG.small(x, **kwargs).xml())
SUP = lambda x, **kwargs: XML(TAG.sup(x, **kwargs).xml())


def getlist(x, index, default=None):
    return x[index] if len(x) > index else default


def alert_gedgat_error(msg):
    alert = DIV(
        BUTTON('&times;', _type='button', _class='close', **{'_data-dismiss':'alert'}),
        STRONG(T('ERROR!')),
        SPAN(T(msg)),
        _class='alert alert-error')
    return alert


def clear_vars_navegate(old_vars, extra_keys=None):
    new_vars = old_vars.copy()
    remove_keys = ['next', '_next', 'previous', \
        '_previous', '_signature', 'origin']
    if extra_keys:
        remove_keys += extra_keys
    for k in remove_keys:
        if new_vars.get(k):
            del new_vars[k]
    return new_vars


def current_url(clear_vars=True):
    new_vars = clear_vars_navegate(request.get_vars) if clear_vars else request.get_vars
    url = URL(r=request, args=request.args, vars=new_vars)
    return url


def breadcrumbs_add(title=None, url=None, reset=None):
    if not title:
        if 'breadcrumbs' in response:
            title = response.breadcrumbs
        else:
            title = response.title+' '+response.subtitle
    if not url:
        url = current_url()

    if reset == None:
        if request.vars.get('_signature'):
            reset = False
        else:
            reset = request.vars.get('origin', '') == 'menu'
        if reset: del request.vars['origin']

    if 'breadcrumbs' in session:
        session.breadcrumbs.add(title, url, reset)
    return


def module11(num):
    base = 9
    factor = 2
    nsum = 0

    for n in reversed(list(num)):
        nsum += int(n) * factor
        factor += 1
        if factor > base:
            factor = 2

    r = nsum % 11
    return 11 - r


def module11_digit(num, replace_as=[0, 10, 11], substitute=1):
    digit = module11(num)
    if digit in replace_as:
        digit = substitute
    return digit


def lookup_url_new(c, f):
    redirect = current_url()
    if '.load' in redirect:
        redirect = request.env.HTTP_REFERER
    return URL(c=c, f=f, args='new', extension='html', vars=dict(redirect=redirect))


def btn_row(href='javascript:void(0);', extra_class=None, title=None, data_id=None, icon=None, caption=None):
    if not extra_class:
        extra_class = ''
    attr = {
        '_href':href,
        '_class':'btn btn-mini '+extra_class,
    }
    if title:
        attr['_title'] = title
        attr['_data-toggle'] = 'tooltip'
    if data_id:
        attr['_data-id'] = data_id
    if icon:
        ico = I(_class=icon)
    else:
        ico = None
    btn = A(caption or '', ico, **attr)
    return btn

def btn_edit_row(href='javascript:void(0);', extra_class=None, title=None, data_id=None, icon=None, caption=None):
    if not title:
        title = T('Edit')
    if not icon:
        icon = 'icon icon-pencil'

    btn = btn_row(href=href, extra_class=extra_class, title=title, data_id=data_id, icon=icon, caption=caption)
    return btn

def btn_remove_row(href='javascript:void(0);', extra_class=None, title=None, data_id=None, icon=None, caption=None):
    if not title:
        title = T('Remove')
    if not icon:
        icon = 'icon icon-trash'

    btn = btn_row(href=href, extra_class=extra_class, title=title, data_id=data_id, icon=icon, caption=caption)
    return btn
