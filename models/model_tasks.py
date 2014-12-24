# -*- coding: utf-8 -*-

from h5_widgets import NicEditorWidget, LookupWidget

class TasksModel(ModelBase):
    name = 'task'

    PRIORITY_SET = {
        'normal':T('Normal'), 
        'warning':T('Warning'),
        'damage':T('Damage'),
        }
    TASK_STATUS_SET = {
        'analysis':T('Analysis'), 
        'development':T('Development'), 
        'test':T('Test'), 
        'released':T('Released'),
        }
    TEST_STATUS_SET = {
        'waiting':T('Waiting'), 
        'success':T('Success'), 
        'error':T('Error'), 
        'retest':T('Retest'),
        }
    TEST_RESULT_SET = {
        'success':T('Success'), 
        'error':T('Error'),
        }

    def define_tables(self):
        self.validate_required(db, ['platform', 'customer'])
        
        def defaultPlatform():
            r = db(db.platform).select().first()
            return r.id        


        def priority_rep(k):
            rep = {
                'normal':'<span class="label">%s</span>',
                'warning':'<span class="label label-warning">%s</span>',
                'damage':'<span class="label label-damage">%s</span>',
                }[k]
            return XML(rep % TasksModel.PRIORITY_SET[k])


        def test_result_rep(k):
            rep = {
                'success':'<span class="label label-success">%s</span>',
                'error':'<span class="label label-important">%s</span>',
                }[k]
            return XML(rep % TasksModel.TEST_RESULT_SET[k])

        field_tags = CommomModel.make_field_tags(db)

        db.define_table('solicitation',
            Field('platform_id', db.platform, label=T('Platform'), readable=False, writable=False),
            Field('customer_id', db.customer, label=T('Customer')),
            Field('customer_detail', 'string', label=T('Customer Detail')),
            Field('priority', 'string', label=T('Priority')),
            Field('subject', 'string', label=T('Subject')),
            Field('content_txt', 'text', label=T('Content')),
            Field('is_new', 'boolean', label=T('Is New?')),
            field_tags,
            migrate='solicitation.table',
            format='%(subject)s')
        db.solicitation.platform_id.requires = IS_IN_DB(db, db.platform, db.platform._format)
        db.solicitation.platform_id.default = defaultPlatform
        db.solicitation.customer_id.requires = IS_IN_DB(db(db.customer.is_active == True), 
            db.customer, db.customer._format, orderby=db.customer.name)
        db.solicitation.customer_id.widget = LookupWidget().widget
        db.solicitation.priority.requires = IS_IN_SET(TasksModel.PRIORITY_SET)
        db.solicitation.priority.default = 'normal'
        db.solicitation.priority.represent = lambda k,row: priority_rep(k)
        db.solicitation.subject.requires = [IS_NOT_EMPTY()]
        db.solicitation.content_txt.widget = NicEditorWidget().widget
        db.solicitation.content_txt.represent = lambda value,row: XML(value, sanitize=False)
        db.solicitation.is_new.default = True


        db.define_table('releases',
            Field('name', 'string', label=T('Name')),
            Field('started', 'datetime', label=T('Started')),
            Field('is_final', 'boolean', label=T('Is Final')),
            migrate="releases.table",
            format='%(name)s')
        db.releases.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'releases.name')]
        db.releases.started.default = request.now
        db.releases.is_final.default = True


        db.define_table('task',
            owner_fields,
            Field('platform_id', db.platform, label=T('Platform'), readable=False, writable=False),
            Field('user_task', db.auth_user, label=T('User Task')),
            Field('priority', 'string', label=T('Priority')),
            Field('status', 'string', label=T('Status')),
            Field('what', 'text', label=T('What?')),
            Field('note', 'text', label=T('Note')),
            Field('test_status', 'string', label=T('Test Status')),
            Field('test_release', db.releases, label=T('Test Release')),
            Field('final_release', db.releases, label=T('Final Release')),
            migrate='task.table',
            format='#%(id)s')
        db.task.platform_id.requires = IS_IN_DB(db, db.platform, db.platform._format)
        db.task.platform_id.default = defaultPlatform
        db.task.user_task.default = auth.user_id
        db.task.user_task.represent = lambda value,row: '%(first_name)s %(last_name)s' % db.auth_user[value]
        db.task.priority.requires = IS_IN_SET(TasksModel.PRIORITY_SET)
        db.task.priority.default = 'normal'
        db.task.priority.represent = lambda value,row: priority_rep(value)
        db.task.status.requires = IS_IN_SET(TasksModel.TASK_STATUS_SET)
        db.task.status.default = 'analysis'
        db.task.status.represent = lambda value, row: TasksModel.TASK_STATUS_SET[value]
        db.task.what.requires = [IS_NOT_EMPTY()]
        db.task.test_status.requires = IS_EMPTY_OR(IS_IN_SET(TasksModel.TEST_STATUS_SET))
        db.task.test_status.represent = lambda value,row: TasksModel.TEST_STATUS_SET[value] if value else ''
        db.task.test_release.requires = IS_EMPTY_OR(IS_IN_DB(db, db.releases, db.releases._format, orderby=db.releases.name))
        db.task.final_release.requires = IS_EMPTY_OR(IS_IN_DB(db, db.releases, db.releases._format, orderby=db.releases.name))
        db.task.what.widget = NicEditorWidget().widget
        db.task.what.represent = lambda value,row: XML(value, sanitize=False)
        db.task.note.widget = NicEditorWidget().widget
        db.task.note.represent = lambda value,row: XML(value, sanitize=False)


        db.define_table('test',
            owner_fields,
            Field('test_result', 'string', label=T('Result')),
            Field('note', 'text', label=T('Note')),
            migrate='test.table',
            format='%(note)s')
        db.test.test_result.requires = IS_IN_SET(TasksModel.TEST_RESULT_SET)
        db.test.test_result.default = 'success'
        db.test.test_result.represent = lambda value,row: test_result_rep(value)
        db.test.note.widget = NicEditorWidget().widget
        db.test.note.represent = lambda value,row: XML(value, sanitize=False)
        return
