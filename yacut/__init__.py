from asgiref.wsgi import WsgiToAsgi
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from settings import Config



app = Flask(
    __name__,
    template_folder='html/templates',
    static_folder='html/static'
)
asgi_app = WsgiToAsgi(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import api_views, error_handlers, models, views
