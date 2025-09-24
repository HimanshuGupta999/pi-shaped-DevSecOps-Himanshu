from flask import Flask
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'SECRET_REMOVED'
DATABASE_URI = 'postgres://user:SECRET_REMOVED@database.server.com:5432/mydb'

@app.route('/')
def home():
    return "Hello, DevSecOps Training!"

if __name__ == '__main__':
    # Port and host configuration for Docker
    app.run(host='0.0.0.0', port=9091)