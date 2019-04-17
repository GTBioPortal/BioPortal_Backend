import os
from application import application
from models import db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

#env_name = os.getenv('FLASK_ENV')
#app = create_app(env_name)


manager = Manager(application)
migrate = Migrate(application, db, compare_type=True)    

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()