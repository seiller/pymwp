import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(os.path.join(here, "pymwp", "version.py")) as fh:
    exec(fh.read())

setuptools.setup(
    name="pymwp",
    version=__version__,
    author="Clément Aubert, Thomas Rubiano, Neea Rusch, Thomas Seiller",
    author_email="nrusch@augusta.edu",
    packages=["pymwp"],
    entry_points={
        "console_scripts": ["pymwp = pymwp.__main__:main"],
    },
    description="Implementation of MWP analysis on C code in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seiller/pymwp",
    project_urls={
        "Bug Tracker": "https://github.com/seiller/pymwp/issues",
        "Documentation": "https://seiller.github.io/pymwp/",
    },
    package_data={"": ["LICENSE"], },
    include_package_data=True,
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Typing :: Typed",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
    ],
    python_requires=">=3.7",
    install_requires=[
        'pycparser ==2.20',
        'progressbar2'
    ]
)
