from setuptools import setup

setup(
    name="pybatchai",
    version='0.0.1',
    install_requires=[
        'Click',
        'coloredlogs',
        'logging',
        'uuid'
    ],
    extras_require={
        'dev': [
            'hypothesis',
            'pylint',
            'pytest'
        ]
    },
    entry_points={
        'console_scripts': ['pybatchai=pybatchai:cli']
    }
)
