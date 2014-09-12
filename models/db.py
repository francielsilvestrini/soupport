# -*- coding: utf-8 -*-

db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])


response.generic_patterns = []
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
# response.static_version = '0.0.0'

from gluon.tools import Auth
auth = Auth(db, controller='user')

from gluon.tools import Crud
crud = Crud(db)

#from gluon.tools import Service
#service = Service()

#from gluon.tools import PluginManager
#plugins = PluginManager()


def _define_auth_model():
    model = UserModel()
    model.define_tables()
    model.create_defaults()
    return

_define_auth_model()


import uuid
oplink_field = Field('oplink', 'string', 
    label=T('Operation Link'), 
    default=uuid.uuid4, 
    writable=False, 
    readable=False)


signature_fields = db.Table(db, 'signature',
    Field('created_on', 'datetime', default=request.now, writable=False, readable=False),
    Field('created_by', db.auth_user, default=auth.user_id, writable=False, readable=False),
    Field('updated_on', 'datetime', update=request.now, writable=False, readable=False),
    Field('updated_by', db.auth_user, update=auth.user_id, writable=False, readable=False))


owner_fields = db.Table(db, 'owner',
    Field('owner_table', 'string', label=T('Owner Table'), writable=False, readable=False),
    Field('owner_key', 'string', label=T('Owner Key'), writable=False, readable=False),
    )


def define_tables():
    ordened_models = [
        TagsModel,
        CommentsModel,
        AttachmentsModel,
        TasksModel,
        ]

    for cls in ordened_models:
        m = cls()
        m.define_tables()
        m.create_defaults()
    return

define_tables()


def _config_painel():
    painel = PainelModel()
    painel.define_tables()
    painel.create_defaults()
    painel.apply_updates()
    return

_config_painel()


'''
## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')
# auth.enable_record_versioning(db)
'''