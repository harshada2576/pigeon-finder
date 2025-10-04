"""
Setup script for Pigeon Finder
"""

from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="pigeon-finder",
    version="1.0.0",
    author="Pigeon Finder Team",
    author_email="team@pigeonfinder.com",
    description="Advanced Duplicate File Detection using Pigeonhole Principle",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/pigeon-finder",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pigeon-finder=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pigeon_finder": ["assets/*", "assets/icons/*"],
    },
)