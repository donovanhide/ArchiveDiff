from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ['archive.sur.ly']
env.user = 'ubuntu'


def restart_webserver():
    "Restart the web server"
    sudo('apache2ctl restart')

def test():
    with settings(warn_only=True):
        result = local('./ArchiveDiff/manage.py test', capture=False)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

def setup():
    with cd('/srv'):
        sudo('rm -Rf /srv/ArchiveDiff')
        sudo('git clone git://github.com/donovanhide/ArchiveDiff.git')
        sudo('rm -Rf /srv/ArchiveIndexer')
        sudo('git clone git://github.com/donovanhide/ArchiveIndexer.git')
    with cd('/srv/ArchiveDiff'):
        sudo('./build.sh')
        
def deploy():
    with cd('/srv/ArchiveDiff'):
        sudo('git pull')
    with cd('/srv/ArchiveIndexer'):
        sudo('git pull')
    restart_webserver()

