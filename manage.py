from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from package import db, app
from package.config import Config
from package.models import *

migrate = Migrate(app, db)
manager = Manager(app)
db.init_app(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
