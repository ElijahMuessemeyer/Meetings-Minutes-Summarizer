#!/usr/bin/env python3
"""
Setup script for Meeting Minutes Summarizer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="meeting-minutes-summarizer",
    version="1.0.1",
    author="Elijah Muessemeyer",
    author_email="elijah@muessemeyer.com",
    description="AI-powered system using Claude/OpenAI to transform meeting transcripts into professional minutes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meeting-minutes-summarizer/meeting-minutes-summarizer",
    packages=find_packages(),
    package_dir={},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "meeting-minutes-summarizer=meeting_minutes_summarizer.main:main",
        ],
    },
    keywords="meeting minutes ai claude openai summarization transcription productivity",
    project_urls={
        "Bug Reports": "https://github.com/meeting-minutes-summarizer/meeting-minutes-summarizer/issues",
        "Source": "https://github.com/meeting-minutes-summarizer/meeting-minutes-summarizer",
        "Documentation": "https://github.com/meeting-minutes-summarizer/meeting-minutes-summarizer#readme",
    },
)