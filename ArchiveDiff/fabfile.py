from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ['archive.sur.ly']
env.user = 'ubuntu'


def restart_webserver():
    "Restart the web server"
    sudo('apache2ctl restart')

def test():
    with settings(warn_only=True):
        result = local('./manage.py test', capture=False)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

def pack():
    local('tar czf /tmp/archivediff.tgz --exclude "data" . ', capture=False)

def prepare_deploy():
    test()
    pack()

def deploy():
    put('/tmp/archivediff.tgz', '/tmp/')
    with cd('/srv/archivediff/'):
        sudo('tar xzf /tmp/archivediff.tgz')
        run('touch app.wsgi')
    restart_webserver()

