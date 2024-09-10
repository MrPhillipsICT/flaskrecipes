import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'yoursecretkey'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'password'
    MYSQL_DB = 'flaskrecipes'
