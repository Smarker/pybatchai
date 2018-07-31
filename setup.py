from setuptools import setup

setup(
    name="pybatchai",
    version='0.1',
    install_requires=[
        'azure',
        'azure-mgmt >= 2.0.0',
        'azure-mgmt-batchai ~= 0.2.0',
        'azure-storage-blob',
        'azure-storage-file',
        'Click',
        'colorama',
        'testresources',
    ],
    entry_points={
        'console_scripts': ['pybatchai=pybatchai:cli']
    }
)
