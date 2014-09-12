# -*- coding: utf-8 -*-

def attachments():
    owner_table = getlist(request.args, 0)
    owner_key  = getlist(request.args, 1)
    if not (owner_table and owner_key):
        response.view = 'others/gadget_error.html'        
        return dict(msg='attachments dont work!')
    
    delete_id = request.vars.get('delete', 0)
    if delete_id:
        db(db.attachments.id == delete_id).delete()

    db.attachments.owner_table.default = owner_table
    db.attachments.owner_key.default = owner_key
    query = ((db.attachments.owner_table == owner_table) & (db.attachments.owner_key == owner_key))

    form = SQLFORM(db.attachments, upload=UPLOAD_URLS['attachments'])

    if request.vars.attachment != None:
        form.vars.name = request.vars.attachment.filename
        form.post_vars = form.vars.name
    form.process()

    content = db(query).select()
    return dict(form=form, content=content)


def attachment_download():
    if not request.args(0) or not request.args[0].isdigit():
        raise HTTP(404)
    id = int(request.args[0])
    import cStringIO 
    import contenttype as c
    s=cStringIO.StringIO() 
     
    (filename,file) = db.attachments.attachment.retrieve(db.attachments[id].attachment)
    s.write(file.read())  
    response.headers['Content-Type'] = c.contenttype(filename)
    response.headers['Content-Disposition'] = "attachment; filename=%s" % filename  
    return s.getvalue()
