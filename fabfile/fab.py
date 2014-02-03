# -*- coding: utf-8 -*-
from fabric.api import env, task, local
from fabric.context_managers import cd
from fabric.operations import require
from misc import _virtualenv as virtualenv, _sudo as sudo, _run as run, _put_template as put_template

@task()
def deploy():
    """
    """
    require('environment', provided_by=('dev', ))
    local('git add .')
    local('git commit -a -m "auto"')
    local('git push')
    with cd(env.project_path):
        run('git pull')
        run('cp settings/development.py settings/local_env.py')
        virtualenv('pip install -r %(PROJECT_PATH)srequirements.txt')

    virtualenv('python manage.py migrate')

    sudo('sudo supervisorctl restart djsocial')
    sudo('sudo supervisorctl restart djsocial_celery')


@task()
def dev():
    """ Set development environment """
    env.environment = 'development'
    env.hosts = ['172.16.178.4', ]
    env.user = 'mmughrabi'
    env.password = 'frogman123'
    env.project_path = '/home/mmughrabi/projects/djsocial-env/djsocial/'
    env.virtualenv = '/home/mmughrabi/projects/djsocial-env'
    env.project_name = 'djsocial'
    env.fabfile = 'fabfile'


@task()
def configure_celery():
    """
    """
    put_template('%(FABFILE)s/templates/celeryd.template', '%(VIRTUALENV)s/celeryd.conf')
    sudo('cp %(VIRTUALENV)s/celeryd.conf /etc/supervisord.d/%(PROJECT_NAME)s_celery.ini')
    sudo('sudo supervisorctl update')
    sudo('sudo supervisorctl restart %(PROJECT_NAME)s_celery')
    run('rm %(VIRTUALENV)s/celeryd.conf')


@task()
def configure_gunicorn():
    """
    """

    put_template('%(FABFILE)s/templates/gunicorn.template', '%(VIRTUALENV)s/gunicorn.conf')
    sudo('cp %(VIRTUALENV)s/gunicorn.conf /etc/supervisord.d/%(PROJECT_NAME)s.ini')
    sudo('sudo supervisorctl update')
    sudo('sudo supervisorctl restart %(PROJECT_NAME)s')
    run('rm %(VIRTUALENV)s/gunicorn.conf')

    put_template('%(FABFILE)s/templates/nginx.template', '%(VIRTUALENV)s/nginx.conf')
    sudo('cp %(VIRTUALENV)s/nginx.conf /etc/nginx/sites/%(PROJECT_NAME)s.conf')
    run('rm %(VIRTUALENV)s/nginx.conf')
    sudo('sudo service nginx restart')

