from setuptools import setup, find_packages
import os

# Read README.md for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from __init__.py if it exists
version = "0.2.0"  # Default version
try:
    with open(os.path.join("NovaSystem", "__init__.py"), "r", encoding="utf-8") as f:
        for line in f.readlines():
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"').strip("'")
                break
except (FileNotFoundError, IOError):
    pass

setup(
    name="novasystem",
    version=version,
    author="NovaSystem Team",
    author_email="info@novasystem.io",
    description="A framework for multi-agent systems with GitHub Docker integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ctavolazzi/NovaSystem",
    project_urls={
        "Bug Tracker": "https://github.com/ctavolazzi/NovaSystem/issues",
        "Documentation": "https://github.com/ctavolazzi/NovaSystem/wiki",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-dotenv>=0.19.0",
        "pydantic>=1.8.0",
        "PyGithub>=1.55",
        "docker>=5.0.0",
        "pytest>=6.0.0",
        "pytest-asyncio>=0.18.0",
    ],
    entry_points={
        "console_scripts": [
            "novasystem=NovaSystem.cli.main:main",
            "novasystem-github-docker=NovaSystem.auto_github_docker:main",
        ],
    },
)