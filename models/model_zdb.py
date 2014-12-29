# -*- coding: utf-8 -*-

db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['sqlite', 'mysql'])

session.connect(request, response, separate=True)

from gluon import current
current.db = db

owner_fields = db.Table(db, 'owner',
    Field('owner_table', 'string', label=T('Owner Table'), writable=False, readable=False),
    Field('owner_key', 'string', label=T('Owner Key'), writable=False, readable=False),
    Field('owner_link', 'string', label=T('Owner Link'), writable=False, readable=False),
    )


from onx_views import PageConfig
if not 'page' in session:
    session.page = PageConfig()

response.generic_patterns = []
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
# response.static_version = '0.0.0'

from gluon.tools import Auth
auth = Auth(db, controller='user')
auth.settings.logout_next = URL(c='default', f='index')

from gluon.tools import Crud
crud = Crud(db)

from gluon.tools import Service
service = Service()

#from gluon.tools import PluginManager
#plugins = PluginManager()


_models_class =  [CommomModel,  ActivityModel]
_models_class += [EntriesModel]
_models_class += [TasksModel]
_models_class += [MULModel]

_models_class += [InventoryModel, VehicleModel, TireControlModel, MaintenanceModel]


from gluon.storage import Storage
app_models = Storage()
app_models.users = UserModel()
app_models.users.model_define()


for cls in _models_class:
    model = cls()
    model.model_define()
    app_models[model.name] = model


app_models.painel = PainelModel()
app_models.painel.model_define()
app_models.painel.apply_updates()


registred_projects = dict()


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