
from flask import Flask, Response

from celery import Celery

app = Flask(__name__)

from kazoo.client import KazooClient, KazooState

zk = KazooClient()



@app.route("/Health")
def health_check():
    return Response(status=200)



def make_celery(app, env):

    if env == "prod":
        zk.set_hosts('zookeeper.default.svc.cluster.local:2181')
        app.config['CELERY_BROKER_URL'] = 'redis://redis-service.default.svc.cluster.local:6379/0'
        app.config['CELERY_RESULT_BACKEND'] = 'redis://redis-service.default.svc.cluster.local:6379/0'

    elif env == "dev":
        zk.set_hosts('host.docker.internal:2181')
        app.config['CELERY_BROKER_URL'] = 'redis://host.docker.internal:6379/0'
        app.config['CELERY_RESULT_BACKEND'] = 'redis://host.docker.internal:6379/0'

    else:
        return None

    zk.start()


    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'], 
        include=['server.api.tasks']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    celery.conf.update(app.config)
    return celery


def create_app():
    #Intialize modules
    from server.api.routes import image
    app.register_blueprint(image, url_prefix="/image/v1")
    return app


celery = make_celery(app, "prod")
