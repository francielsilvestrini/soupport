# -*- coding: utf-8 -*-

from gluon.custom_import import track_changes
track_changes(True)

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


def current_url():
    url = URL(r=request, args=request.args, vars=request.vars)
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

