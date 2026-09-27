#!/usr/bin/env python
"""Setup configuration for code-assistant package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="code-assistant",
    version="0.1.0",
    author="Olga Moreira",
    author_email="olga.moreira@gmail.com",
    description="Local Coding Assistant with code generation, debugging, and patching capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/omoreira/code_assistant",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
            "pylint>=2.13",
            "ipython>=8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "code-assistant=code_starter.starterfile_creator:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
