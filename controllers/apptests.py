# -*- coding: utf-8 -*-

def index():
    fname = os.path.join(request.folder, 'languages','pt-br.py')
    ins = open( fname, "r" )
    array = []
    separator = '\': \''
    for i, line in enumerate(filter(lambda s: separator in s, ins)):

        fields = line.split('\': \'')
        original = fields[0][1:]
        language = fields[1][0:-3]

        array.append( (i, original, language) )
    ins.close()

    rows = []
    for i, original, language in array:
        rows += [TR(
            P(original),
            TEXTAREA(language, _name='key_%s'%i)
            )]
    form = FORM(TABLE(rows, _class='table table-bordered'), INPUT(_type='submit'))
    if form.process().accepted:
        print 'sucess'

    return dict(content=form)


def todo():
    session.page.header_files['select2.css'] = URL('static','assets/select2-3.5.1/select2.css')
    session.page.footer_files['select2.min.js'] = URL('static','assets/select2-3.5.1/select2.min.js')

    return dict()
