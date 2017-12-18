from setuptools import setup

setup(
    name='MeetMe',
    packages=['MeetMe'],
    include_package_data=True,
    install_requires=[
        'flask',
        'werkzeug,',
        'arrow',
        'httplib2',
        'oauth2client',
        'requests',
        'pendulum',
        'flask_oauth',
        'google-api-python-client'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
