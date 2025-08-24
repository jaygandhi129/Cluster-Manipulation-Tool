"""
Setup script for the Cluster Manipulation Tool.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cluster-manipulation-tool",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Streamlit application for visualizing and manipulating cluster data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cluster-manipulation-tool",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/cluster-manipulation-tool/issues",
        "Documentation": "https://github.com/yourusername/cluster-manipulation-tool#readme",
        "Source Code": "https://github.com/yourusername/cluster-manipulation-tool",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Streamlit",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.4.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.2.0",
            "mkdocstrings[python]>=0.22.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cluster-tool=app.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": ["*.py"],
        "data": ["*.json"],
    },
    zip_safe=False,
    keywords="streamlit, cluster, visualization, data-manipulation, flow-diagram",
)
