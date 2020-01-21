import os
import json

with open('/etc/config.json') as config_file:
    config = json.load(config_file)

    class Config:
        SECRET_KEY = config.get('SECRET_KEY')
        SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
        MAX_CONTENT_LENGTH = 4096 * 1024
        MAIL_SERVER = 'smtp.googlemail.com'
        MAIL_PORT = 587
        MAIL_USE_TLS = True
        EMAIL_USER = config.get('EMAIL_USER')
        EMAIL_PASS = config.get('EMAIL_PASS')
