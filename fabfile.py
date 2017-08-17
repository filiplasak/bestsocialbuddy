from fabric.api import *

# the user to use for the remote commands
env.user = 'bestsocialbuddy'
# the servers where the commands are executed
env.hosts = ['1.2.3.4']
env.port = 70

PROD_CONFIG_FILE = 'config_prod.py'
PROD_BASE_FOLDER = '/home/bestsocialbuddy'

BASE_CONFIG_FOLDER = 'config/app'
BASE_ENV_FOLDER = 'config/env'

WSGI_FILE = 'wsgi.py'


def pack():
    # build the package
    local('python setup.py sdist --formats=gztar', capture=False)


def deploy():
    # figure out the package name and version
    dist = local('python setup.py --fullname', capture=True).strip()
    filename = '%s.tar.gz' % dist

    # upload the package to the temporary folder on the server
    put('dist/%s' % filename, '/tmp/%s' % filename)

    # install the package in the application's virtualenv with pip
    run('%s/env/bin/pip install /tmp/%s' % (PROD_BASE_FOLDER, filename))

    # remove the uploaded package
    run('rm -r /tmp/%s' % filename)

    # touch the .wsgi file to trigger a reload in mod_wsgi
    run('touch %s/deploy/%s' % (PROD_BASE_FOLDER, WSGI_FILE))

    # restart gunicorn
    run('sudo /bin/systemctl restart bestsocialbuddy')


def prodconfig():
    # upload configs
    put('%s/%s' % (BASE_CONFIG_FOLDER, PROD_CONFIG_FILE), '%s/deploy/%s' % (PROD_BASE_FOLDER, PROD_CONFIG_FILE))
    put('%s/%s' % (BASE_ENV_FOLDER, WSGI_FILE), '%s/deploy/%s' % (PROD_BASE_FOLDER, WSGI_FILE))
    put('config/env/bestsocialbuddy.service', '%s/deploy/bestsocialbuddy.service' % PROD_BASE_FOLDER)

    # touch wsgi file - TODO: this should trigger restart of gunicorn/service
    # run('touch %s/deploy/%s' % (PROD_BASE_FOLDER, WSGI_FILE))

    # restart gunicorn
    run('sudo /bin/systemctl restart bestsocialbuddy')


def test():
    # test run of fabric
    run('hostname')
