# -*- coding: utf-8 -*-
from gluon.html import XML

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


from urlparse import urlparse
class Breadcrumbs(object):

    crud_actions = ['new', 'read', 'update', 'delete', 'select']

    def __init__(self):
        self.items = []
        return

    def reset(self, home_title, home_url):
        self.items = [(home_title, home_url)]

    def delete_current(self):
        del self.items[-1]

    def delete_item(self, index):
        while len(self.items) > index:
            self.delete_current()

    def add(self, title, url, reset=False):
        if not url:
            return

        if reset:
            self.delete_item(1)
        else:
            for i, (t, u) in enumerate(self.items):
                if urlparse(u).path == urlparse(url).path:
                    self.delete_item(i)
                    break

        last = self.last_url()
        if last:
            last = urlparse(last).path.split('/')
            curr = urlparse(url).path.split('/')
            last_action = last[4] if len(last) > 4 else 'select'
            curr_action = curr[4] if len(curr) > 4 else 'select'
            if (last[:4] == curr[:4]) and (last_action != 'select') and (curr_action in Breadcrumbs.crud_actions):
                self.delete_current()

        self.items.append( (title, url) )
        return

    def last_url(self):
        if len(self.items):
            t, u = self.items[-1]
        else:
            u = None
        return u

    def prior_url(self):
        if len(self.items)>1:
            t, u = self.items[-2]
        else:
            u = None
        return u

    def last_url_parts(self):
        if not self.last_url():
            last = ['' for i in range(5)]
        else:
            last = urlparse( self.last_url() ).path.split('/')
        parts = dict(
            controller=last[2],
            function=last[3],
            args=last[4:]
            )
        return parts
