from setuptools import setup
from setuptools import find_packages

setup(
    name='tally',
    version='0.1',
    description='Keep tallies',
    packages=find_packages(
        exclude='tests',
    ),
    install_requires=[
        'click',
        'sqlalchemy',
        'questionary',
    ],
    entry_points = {
        'console_scripts': ['tally=tally.cli:tally'],
    },
    zip_safe=False,
    # package_data={
    #     '': ['data/default.yml'],
    #     '': ['data/anonymous-pro.als'],
    # },
    # include_package_data=True,
)
