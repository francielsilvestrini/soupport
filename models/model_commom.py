# -*- coding: utf-8 -*-

from h5_widgets import TagsInputWidget

class CommomModel(ModelBase):
    name = 'attachments'

    def define_tables(self):
        db.define_table('attachments',
            owner_fields,
            Field('attachment', 'upload', label=T('Attachment'), uploadfolder=UPLOAD_URLS['attachments'], autodelete=True),
            Field('name', 'string', label=T('Name'), readable=False, writable=False),
            Field('file_size', 'double', label=T('Size'), readable=False, writable=False),
            migrate='attachments.table',
            format='%(name)s')
        db.attachments.file_size.compute = lambda row: path.getsize(path.join(UPLOAD_URLS['attachments'],row.attachment))/1024
        self.set_table_defaults(db.attachments, 0)


        db.define_table('comments',
            owner_fields,
            Field('comment_str', 'string', label=T('Comment')),
            migrate='comments.table',
            format='%(comment)s')

        db.define_table('tag',
            Field('name', 'string', label=T('Name')),
            migrate="tag.table",
            format='%(name)s')
        db.tag.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'tag.name')]
        self.set_table_defaults(db.comments, 0)


        db.define_table('sequence_ticket',
            Field('target', 'string', label=T('Target')),
            Field('ticket_left', 'string', label=T('Left')),
            Field('ticket_right', 'string', label=T('Right')),
            Field('ticket_size', 'integer', label=T('Size')),
            Field('sequence', 'string', label=T('Sequence')),
            migrate="sequence_ticket.table",
            format='%(sequence)s')
        self.set_table_defaults(db.sequence_ticket, 0)
        return


    @staticmethod
    def make_field_tags(db):
        def _tag_represent(value):
            if value:
                rep = [A(SPAN(name, _class='label label-info'), SPAN(' '),
                    _href='javascript:void(0);', _class='tag') for name in value.split(',')]
            else:
                rep = []
            return DIV(rep)

        field_tags = Field('tags', 'string',
            label=T('Tags'),
            widget=TagsInputWidget(url=URL(c='tags', f='tag_data.json', host=True)).widget,
            represent=lambda value,row: _tag_represent(value)
            )

        return field_tags

    #--------------------------------------------------------------------------
    # BEGIN BUSINESS RULES

    @staticmethod
    def sequence_ticket(target, left='', right=''):
        painel = db(db.painel.id > 0).select().first()

        defs = table_default_values(db.sequence_ticket)
        defs['target'] = target
        defs['ticket_left'] = left
        defs['ticket_right'] = right
        defs['ticket_size'] = painel.ticket_size
        ticket_id = db.sequence_ticket.insert(**defs)

        defs['ticket_id'] = str(ticket_id).zfill(defs['ticket_size'])
        sequence = '%(ticket_left)s%(ticket_id)s%(ticket_right)s' % defs

        db(db.sequence_ticket.id == ticket_id).update(sequence=sequence)
        return sequence

    # END BUSINESS RULES
    #--------------------------------------------------------------------------


