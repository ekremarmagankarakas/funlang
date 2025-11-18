from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# Read requirements
def read_requirements():
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="funlang",
    version="0.1.0",
    description="A simple, fun programming language with multilingual support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/funlang",
    packages=find_packages(),
    py_modules=["main", "run"],
    include_package_data=True,
    package_data={
        "": ["configs/*.json"],
    },
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "funlang=main:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
