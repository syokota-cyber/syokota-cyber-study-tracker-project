#!/usr/bin/env python3
"""
Setup script for StudyTracker project.
"""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="study-tracker",
    version="0.1.0",
    author="StudyTracker Team",
    author_email="team@studytracker.com",
    description="A personal study progress and goal management application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/syokota-cyber/study-tracker-project",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "bandit>=1.7.0",
            "safety>=2.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "study-tracker=cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 