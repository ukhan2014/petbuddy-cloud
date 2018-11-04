from flask import Flask

print("start")

app = Flask(__name__)

app.secret_key = 'development key'

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'contact@example.com'
app.config["MAIL_PASSWORD"] = 'your-password'

print("middle")

from petbuddy_cloud.routes import mail
mail.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://petbuddycloud:h9%$mYD!QPgVz@localhost/development'

from petbuddy_cloud.models import db
db.init_app(app)

import petbuddy_cloud.routes

print("init complete")
