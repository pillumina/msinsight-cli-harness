"""
MindStudio Insight CLI - PyPI Package Setup

This setup.py configures the cli-anything-msinsight package for installation.
"""

from setuptools import setup, find_namespace_packages
import os

# Read version from package
version = "1.0.0"
try:
    with open(os.path.join(os.path.dirname(__file__),
                           "cli_anything", "msinsight", "__init__.py")) as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"\'')
                break
except:
    pass

# Read README for long description
long_description = ""
readme_path = os.path.join(os.path.dirname(__file__),
                           "cli_anything", "msinsight", "README.md")
if os.path.exists(readme_path):
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="cli-anything-msinsight",
    version=version,
    author="MindStudio Team",
    author_email="mindstudio@huawei.com",
    description="Command-line interface for MindStudio Insight - Performance Analysis Tool for Ascend AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitcode.com/Ascend/msinsight",
    license="Mulan PSL v2",

    # Use namespace packages (cli_anything/ has no __init__.py)
    packages=find_namespace_packages(include=["cli_anything.*"]),

    # Include package data (README, SKILL.md, etc.)
    package_data={
        "cli_anything.msinsight": [
            "README.md",
            "skills/*.md",
        ],
    },

    # Python dependencies
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
        "websocket-client>=1.0.0",
    ],

    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },

    # Entry points - makes CLI available in PATH
    entry_points={
        "console_scripts": [
            "cli-anything-msinsight=cli_anything.msinsight.msinsight_cli:main",
        ],
    },

    # Python version requirement
    python_requires=">=3.10",

    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Mulan Permissive Software License v2 (MulanPSL-2.0)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],

    # Keywords for searchability
    keywords=[
        "cli",
        "mindstudio",
        "insight",
        "ascend",
        "ai",
        "performance",
        "analysis",
        "profiling",
        "optimization",
        "huawei",
    ],

    # Project URLs
    project_urls={
        "Bug Tracker": "https://gitcode.com/Ascend/msinsight/issues",
        "Documentation": "https://msinsight.readthedocs.io/",
        "Source Code": "https://gitcode.com/Ascend/msinsight",
    },
)
