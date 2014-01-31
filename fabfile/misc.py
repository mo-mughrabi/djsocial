# -*- coding: utf-8 -*-
from fabric.api import env, task, run
from fabric.context_managers import cd
from fabric.operations import put, sudo


def _sudo(params):
    """
    Run command as root
    """
    command = _render(params)
    sudo(command)


def _virtualenv(command):
    """ """
    with cd(env.project_path):
        run('source ' + env.virtualenv + '/bin/activate && ' + _render(command))


def _run(params):
    """
    Runs command with active user
    """
    command = _render(params)
    run(command)


def _render(template, context=None):
    """
    Does variable replacement
    """
    if context is None:
        context = dict((k.upper(), v) for k, v in env.iteritems())
        context.update({'CELERY_DEFAULT_QUEUE': 'ts'})
    return template % context


def _write_to(string, path):
    """
    Writes a string to a file on the server
    """
    return "echo '" + string + "' > " + path


def _put_template(template, dest):
    """
    Same as _put() but it loads a file and does variable replacement
    """
    f = open(_render(template), 'r')
    template = f.read()
    run(_write_to(_render(template), _render(dest)))


def _put(template, dest):
    """
    Moves a file from local computer to server
    """
    put(_render(template), _render(dest))