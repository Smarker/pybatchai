from setuptools import setup

setup(
    name="pybatchai",
    version='0.1',
    py_modules=['hello'],
    install_requires=[
        'Click',
        'azure',
        'azure-storage-blob',
        'azure-storage-file',
        'coloredlogs',
        'logging',
        'azure-mgmt-batchai >= 2.0.0',
        'python_version >= 3.6'
    ],
    entry_points='''
        easycluster=easycluster:cli
    '''
)