import sys
sys.path.append('/home/ubuntu/.local/bin')
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello from PetBuddy Cloud!'

if __name__ == '__main__':
  app.run()
