# setup.py

from setuptools import find_packages, setup

setup(
    name="temporal-kb",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "pyyaml>=6.0",
        "python-dateutil>=2.8.0",
        "pyperclip>=1.8.0",
        "gitpython>=3.1.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "chromadb>=0.4.0",
        "sentence-transformers>=2.2.0",
    ],
    entry_points={
        'console_scripts': [
            'kb=kb.cli.main:main',
        ],
    },
    python_requires='>=3.10',
)
