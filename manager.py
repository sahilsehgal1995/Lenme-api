import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from src import api, db, ma, create_app, configs, bp, security, admin, elastic_store, mail

config = os.environ.get('PYTH_SRVR')

config = configs.get(config, 'default')

extensions = [mail, api, db, ma, security, admin, elastic_store]
bps = [bp]

app = create_app(__name__, config, extensions=extensions, blueprints=bps)

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.shell
def _shell_context():
    return dict(
        app=app,
        db=db,
        ma=ma,
        config=config
        )

if __name__ == "__main__":
    # app.run(host='0.0.0.0', debug=True)
    manager.run()
