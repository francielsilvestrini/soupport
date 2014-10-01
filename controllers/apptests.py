# -*- coding: utf-8 -*-

def index():
    import re
    myString = "This is my tweet check it out http://127.0.0.1:8000/soupport/apptests/"
    match = re.search("(?P<url>https?://[^\s]+)", myString)
    if match is not None: 
        print match.group("url")

    return dict()


def todo():
    session.page.header_files['select2.css'] = URL('static','assets/select2-3.5.1/select2.css')
    session.page.footer_files['select2.min.js'] = URL('static','assets/select2-3.5.1/select2.min.js')

    return dict()
