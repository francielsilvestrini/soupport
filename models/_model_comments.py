# -*- coding: utf-8 -*-

from onx_model import ModelBase

class CommentsModel(ModelBase):
    name = 'comments'

    def define_tables(self):
        db.define_table('comments',
            owner_fields,
            oplink_field,
            signature_fields,
            Field('comment_str', 'string', label=T('Comment')),
            migrate='comments.table',
            format='%(comment)s')       
        return  
