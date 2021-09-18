from setuptools import setup
from bqrepl import __version__

with open("requirements.txt", "r") as f:
    requirements = [x.strip() for x in f.readlines()]

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="bqrepl",
    version=__version__,
    license="MIT",
    author="Bartosz Pieniak",
    author_email="bartosz.pieniak@gmail.com",
    description="REPL for Big Query",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bartekpi/bqrepl",
    packages=["bqrepl"],
    install_requires=requirements,
    python_requires=">=3.6",
    entry_points="""
        [console_scripts]
        bqrepl=bqrepl.main:cli
    """,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: SQL",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
    ],
)
