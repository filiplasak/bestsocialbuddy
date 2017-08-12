from fabric.api import *

# the user to use for the remote commands
env.user = 'bestsocialbuddy'
# the servers where the commands are executed
env.hosts = ['1.2.3.4']
env.port = 70

BASE_FOLDER='/home/bestsocialbuddy'
PROD_CONFIG_FILE='config_prod.py'
WSGI_FILE='wsgi.py'


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
    run('%s/env/bin/pip install /tmp/%s' % (BASE_FOLDER, filename))

    # remove the uploaded package
    run('rm -r /tmp/%s' % filename)

    # touch the .wsgi file to trigger a reload in mod_wsgi
    run('touch %s/deploy/%s' % (BASE_FOLDER, WSGI_FILE))


def prodconfig():
    # upload configs
    put('%s' % PROD_CONFIG_FILE, '%s/deploy/%s' % (BASE_FOLDER, PROD_CONFIG_FILE))
    put('config/%s' % WSGI_FILE, '%s/deploy/%s' % (BASE_FOLDER, WSGI_FILE))
    put('config/bestsocialbuddy.service', '%s/deploy/bestsocialbuddy.service' % BASE_FOLDER)
    run('touch %s/deploy/%s' % (BASE_FOLDER, WSGI_FILE))


def test():
    # test run of fabric
    run('hostname')
