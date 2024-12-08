from setuptools import setup, find_packages

setup(
    name="ns-bytesize",
    version="0.1",
    packages=find_packages(where='.', exclude=['tests*']),
    package_dir={'': '.'},
    install_requires=[
        "requests>=2.32.3",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
    ],
    extras_require={
        'dev': [
            'pytest>=8.3.4',
            'pytest-asyncio>=0.24.0',
            'pytest-cov>=6.0.0',
            'pytest-mock>=3.12.0',
        ],
    },
    python_requires=">=3.8",
)
