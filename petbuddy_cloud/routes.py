from petbuddy_cloud import app
from flask import render_template, request, flash, session, url_for, redirect
from petbuddy_cloud.forms import ContactForm, SignupForm, SigninForm
from flask_mail import Message, Mail
from petbuddy_cloud.models import db, User
from sqlalchemy.orm import exc as orm_exc
import time
import json

mail = Mail()

def sendWelcomeEmail(email_address_str, serial_no):
  print("sendWelcomeEmail: add="+email_address_str+" ser="+serial_no)
  msg_data = """
    Welcome to PetBuddy!
    You are all signed up as a PetBuddy user and
    your device is now registered!

    Your device serial is %s.
  """ % (serial_no)
  msg = Message("Welcome", sender='PetBuddy Cloud',
                recipients=[email_address_str])
  msg.body = """
      From: PetBuddy Cloud <petbuddy.cloud@gmail.com>
      %s """ % (msg_data)
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
      msg = Message(form.subject.data, sender='contact@example.com',
                    recipients=['your_email@example.com'])
      msg.body = """
      From: %s <%s>
      %s
      """ % (form.name.data, form.email.data, form.message.data)
      mail.send(msg)

      return render_template('contact.html', success=True)

  elif request.method == 'GET':
    return render_template('contact.html', form=form)

@app.route('/devreg', methods=['GET', 'POST'])
def devreg():
  print("devreg()")
  ip = request.environ['REMOTE_ADDR']
  state = True

  if request.method == 'POST':
    data = request.get_data()
    print( data)
    jdata = json.loads(data)
    if all(x not in jdata for x in ['fname','lname','serial',
           'email','pwd']):
      print("registration info incomplete")
      state = False

  print("state is now " + str(state))
  if state:
    newuser = User(jdata['serial'], str(time.time()), str(ip), jdata['email'],
                   jdata['pwd'], jdata['fname'], jdata['lname'])
    register(newuser)
    return "registration complete\n"
    
  return "registration failure, incomplete info"


def register(usr):
  db.session.add(usr)
  db.session.commit()

  sendWelcomeEmail(usr.email, usr.serial_no)
  session['email'] = usr.email
	
@app.route('/signup', methods=['GET', 'POST'])
def signup():
  print("signup()")

  form = SignupForm()
  if 'email' in session:
    return redirect(url_for('profile')) 

  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signup.html', form=form)
    else:
      print("fname = " + form.fname.data)
      print("lname = " + form.lname.data)
      print("ser = " + form.serial_no.data)
      print("lping = " + form.last_ping.data)
      print("ip = " + form.ip_add.data)
      print("email = " + form.email.data)
      print("pwd = " + form.password.data)
      newuser = User( form.serial_no.data, form.last_ping.data,
                      form.ip_add.data, form.email.data, form.password.data,
                      form.fname.data, form.lname.data)

      register(newuser)      
      return redirect(url_for('profile'))

  elif request.method == 'GET':
    return render_template('signup.html', form=form)


@app.route('/ping/<serialno>')
def ping(serialno):
  ip = request.environ['REMOTE_ADDR']
  print("remote ip is " + ip)

  ping_time = int(time.time())
  print("got ping from pbd " +str(serialno)+" at "+str(ping_time))

  # update the last ping time of the pbd unit
  try:
    user = User.query.filter_by( serial_no = (str(serialno)) ).one()
    user.last_ping =  ping_time
    db.session.commit()
    print("updated last_ping time of pbd serial "+user.serial_no+" to "
          +str(ping_time))
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


# Future additions:

# @app.route('/feed', methods=['GET', 'POST'])
# def feed():
#   print("feed()")
#   ip = request.environ['REMOTE_ADDR']
#   state = True
#
#   if request.method == 'POST':
#     data = request.get_data()
#     print data
#     jdata = json.loads(data)
#     if all(x not in jdata for x in ['serial',
#            'authtoken']):
#       print("Don't know which device to turn servo on")
#       state = False
#     else if(!do_auth(serialno, authtoken)):
#       print("auth failed")
#       state = False
#
#   print("state is now " + str(state))
#   if state:
#     turnServo(jdata['serial'], str(ip), jdata['authtoken'])
#     return "turnServo command dispatched\n"
#
#   return "info incomplete or auth not accepted"

# Get a pbd to snap a photo
#@app.route('/snap', methods=['GET', 'POST'])
#def snap():
#  print("snap()")

# Get a pbd to open feed door



# Get a pbd to close feed door


# Factory reset a pbd


# Reboot a pbd



# def turnServo(serialno, authentication):
#   print(turnServo)

# def do_auth(serialno, authtoken):
#   print("Do authentication of " + serialno)
