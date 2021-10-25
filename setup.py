"""BorgAPI Package Setup"""
import setuptools

from batchrenamer import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="batchrenamer",
    version=__version__,
    author="Sean Slater",
    author_email="seanslater@whatno.io",
    description="Rename multiple files with the same rules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spslater/batchrenamer",
    license="MIT License",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
        "Topic :: System :: Filesystems",
        "Environment :: Console",
    ],
    keywords="filesystem files rename batch",
    python_requires=">=3.7",
)
