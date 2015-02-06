# -*- coding: utf-8 -*-

def index():
    return dict()


def todo():
    session.page.header_files['select2.css'] = URL('static','assets/select2-3.5.1/select2.css')
    session.page.footer_files['select2.min.js'] = URL('static','assets/select2-3.5.1/select2.min.js')

    return dict()
