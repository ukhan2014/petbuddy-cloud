from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
  __tablename__ = 'pbdusrs'
  device_id = db.Column(db.Integer, primary_key = True)
  serial_no = db.Column(db.String(100))
  last_ping = db.Column(db.Integer)
  ip_add = db.Column(db.String(100))
  email = db.Column(db.String(120), unique=True)
  pwdhash = db.Column(db.String(54))
  
  def __init__(self, serial_no, last_ping, ip_add, email, password):
    self.serial_no = serial_no
    self.last_ping = last_ping
    self.ip_add = ip_add
    self.email = email.lower()
    self.set_password(password)
    
  def set_password(self, password):
    self.pwdhash = generate_password_hash(password)
  
  def check_password(self, password):
    return check_password_hash(self.pwdhash, password)
