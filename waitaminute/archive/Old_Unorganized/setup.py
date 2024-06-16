from setuptools import setup, find_packages

setup(
    name='NovaSystem',
    version='0.0.1',
    author='Christopher Tavolazzi',
    author_email='ctavolazzi@gmail.com',
    description='AI CLI tool for NovaSystem SDK',
    long_description=open('README.md').read(),
    url='https://github.com/ctavolazzi/NovaSystem',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    include_package_data=True,
    install_requires=[
        'typer',
    ],
    entry_points={
        'console_scripts': [
            'novasystem=novasystem.cli:cli',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
