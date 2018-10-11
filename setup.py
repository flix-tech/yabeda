from setuptools import setup, find_packages

setup(
    name='yabeda',
    version='0.1',

    description="Yabeda",
    long_description="""
    A tool that sends deployment notifications from Gitlab CI to Slack.
    """,
    url="https://github.com/flix-tech/yabeda",

    author="Flixtech",

    license='MIT',

    python_requires='>=3.6',

    packages=find_packages(),

    install_requires=[
        'flask',
        'pytest',
        'pytest-cov',
        'python-gitlab',
        'slackclient',
        'flasgger',
        'ciso8601',
        'python-dateutil',
        'uwsgi'
    ],
)
