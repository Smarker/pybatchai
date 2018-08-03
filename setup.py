from setuptools import setup

setup(
    name="pybatchai",
    version='0.0.1',
    install_requires=[
        'azure',
        'azure-mgmt >= 2.0.0',
        'Click',
        'coloredlogs',
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
