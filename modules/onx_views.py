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
