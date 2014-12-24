# -*- coding: utf-8 -*-

class ActivityModel(ModelBase):
    name = 'activity'
    
    TODO_STATUS_SET = {
        'waiting':T('Waiting'), 
        'done':T('Done'),
        'canceled':T('Canceled'),
        }

    def define_tables(self):
        def todo_status_rep(value, row):
            rep = {
                'waiting':'<span class="spt-status tooltip-top" title="%s"><i class="fa fa-flag"></i></span>',
                'done':'<span class="spt-status tooltip-top" title="%s"><i class="fa fa-thumbs-up"></i></span>',
                'canceled':'<span class="spt-status tooltip-top" title="%s"><i class="fa fa-times"></i></span>',
                }[value]
            return XML(rep % ActivityModel.TODO_STATUS_SET[value])

        def todo_content_rep(value, row):
            import re
            match = re.search('(?P<url>https?://[^\s]+)', value)
            if match is not None: 
                url = match.group('url')
                content = value.replace(url, '')
                if content == '':
                    content = value
                return SPAN(A(content, _href=url, _target='_blank'))
            else:
                return value

        db.define_table('activity_todo',
            owner_fields,
            Field('content', 'string', label=T('Content')),
            Field('status', 'string', label=T('Status')),
            migrate='activity_todo.table',
            format='%(content)s')
        db.activity_todo.content.requires = [IS_NOT_EMPTY()]
        db.activity_todo.content.represent = lambda value, row: todo_content_rep(value, row)
        db.activity_todo.status.requires = IS_IN_SET(ActivityModel.TODO_STATUS_SET)
        db.activity_todo.status.default = 'waiting'
        db.activity_todo.status.represent = lambda value, row: todo_status_rep(value, row)

        '''

        db.define_table('activity_msg',
            owner_fields,
            oplink_field,
            signature_fields,
            Field('subject', 'string', label=T('Subject')),
            Field('content', 'text', label=T('Content')),
            Field('compose_status', 'string', label=T('Compose Status')),
            Field('important', 'boolean', label=T('Important')),
            migrate='activity_msg.table',
            format='%(subject)s')
        db.activity_msg.subject.requires = [IS_NOT_EMPTY()]
        db.activity_msg.compose_status.requires = IS_IN_SET(ActivityModel.COMPOSE_STATUS_SET)
        db.activity_msg.compose_status.default = 'waiting'
        db.activity_msg.compose_status.represent = lambda value, row: ActivityModel.COMPOSE_STATUS_SET[value]
        db.activity_msg.important.default = True


            Field('read_status', 'string', label=T('Read Status')),
            Field('for_users', 'list:reference auth_user', label=T('For Users')),
        '''
        return  
