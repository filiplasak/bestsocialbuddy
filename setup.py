from setuptools import setup

setup(
    name='best-social-buddy',
    version='1.1.3',
    long_description=__doc__,
    packages=['app'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fabric3',
        'click==6.7',
        'facebook-sdk==2.0.0',
        'Flask==0.12.1',
        'Flask-Login==0.4.0',
        'Flask-SQLAlchemy==2.2',
        'itsdangerous==0.24',
        'Jinja2==2.9.6',
        'MarkupSafe==1.0',
        'requests==2.13.0',
        'SQLAlchemy==1.1.9',
        'Werkzeug==0.12.1'
    ]
)
