from setuptools import setup, find_packages

setup(
    name='NovaSystem',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # List your project dependencies here
    ],
    entry_points='''
        [console_scripts]
        novasystem=novasystem:main
    ''',
)
