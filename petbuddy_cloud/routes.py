from petbuddy_cloud import app
from flask import render_template, request, flash, session, url_for, redirect
from forms import ContactForm, SignupForm, SigninForm
from flask_mail import Message, Mail
from models import db, User
from sqlalchemy.orm import exc as orm_exc
import time
#import sys

mail = Mail()
#sys.stdout = open('/home/pi/development/petbuddy_cloud/logs.txt', 'w')

def sendWelcomeEmail(email_address_str, serial_no):
  msg_data = """
    Welcome to PetBuddy!
    You are all signed up as a PetBuddy user and
    your device is now registered!

    Your device serial is %s.
  """ % (serial_no)
  msg = Message("Welcome", sender='PetBuddy Cloud', recipients=[email_address_str])
  msg.body = """
      From: PetBuddy Cloud <petbuddy.cloud@gmail.com>
      %s
      """ % (msg_data)
  mail.send(msg)

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
  form = ContactForm()

  if request.method == 'POST':
    if form.validate() == False:
      flash('All fields are required.')
      return render_template('contact.html', form=form)
    else:
      msg = Message(form.subject.data, sender='contact@example.com', recipients=['your_email@example.com'])
      msg.body = """
      From: %s <%s>
      %s
      """ % (form.name.data, form.email.data, form.message.data)
      mail.send(msg)

      return render_template('contact.html', success=True)

  elif request.method == 'GET':
    return render_template('contact.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  form = SignupForm()

  if 'email' in session:
    return redirect(url_for('profile')) 

  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signup.html', form=form)
    else:
      newuser = User(form.serial_no.data, form.last_ping.data, form.ip_add.data, form.email.data, form.password.data)
      db.session.add(newuser)
      db.session.commit()

      sendWelcomeEmail(form.email.data, form.serial_no.data)
      session['email'] = newuser.email
      return redirect(url_for('profile'))

  elif request.method == 'GET':
    return render_template('signup.html', form=form)


@app.route('/ping/<serialno>')
def ping(serialno):
  ping_time = int(time.time())
  print("got ping from pbd " +str(serialno)+" at "+str(ping_time))

  # update the last ping time of the pbd unit
  try:
    user = User.query.filter_by( serial_no = (str(serialno)) ).one()
    user.last_ping =  ping_time
    db.session.commit()
    print("updated last_ping time of pbd serial "+user.serial_no+" to "+str(ping_time))
  except(orm_exc.NoResultFound):
    print("this pbd was not found, ignore")
  except(orm_exc.MultipleResultsFound):
    print("ERROR: more than one pbd found, sno="+str(serialno))

  return render_template('profile.html')


@app.route('/profile')
def profile():

  if 'email' not in session:
    return redirect(url_for('signin'))

  user = User.query.filter_by(email = session['email']).first()

  if user is None:
    return redirect(url_for('signin'))
  else:
    return render_template('profile.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
  form = SigninForm()

  if 'email' in session:
    return redirect(url_for('profile'))

  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signin.html', form=form)
    else:
      session['email'] = form.email.data
      return redirect(url_for('profile'))

  elif request.method == 'GET':
    return render_template('signin.html', form=form)

@app.route('/signout')
def signout():

  if 'email' not in session:
    return redirect(url_for('signin'))

  session.pop('email', None)
  return redirect(url_for('home'))
