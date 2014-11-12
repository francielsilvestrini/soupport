# -*- coding: utf-8 -*-

from onx_model import ModelBase

class AttachmentsModel(ModelBase):
    name = 'attachments'

    def define_tables(self):
        db.define_table('attachments',
            owner_fields,
            oplink_field,
            signature_fields,
            Field('attachment', 'upload', label=T('Attachment'), uploadfolder=UPLOAD_URLS['attachments'], autodelete=True),
            Field('name', 'string', label=T('Name'), readable=False, writable=False),
            Field('file_size', 'double', label=T('Size'), readable=False, writable=False),
            migrate='attachments.table',
            format='%(name)s')
        db.attachments.file_size.compute = lambda row: path.getsize(path.join(UPLOAD_URLS['attachments'],row.attachment))/1024
        return  
